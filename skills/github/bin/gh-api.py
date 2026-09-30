#!/usr/bin/env python3
"""Call the GitHub REST API with the stored custom.github credential.

Usage:
    gh-api.py GET <path> [json-body-file]
    gh-api.py POST <path> [json-body-file]
    gh-api.py PATCH <path> [json-body-file]
    gh-api.py PUT <path> [json-body-file]
    gh-api.py DELETE <path>

<path> is relative to https://api.github.com/, e.g. "user" or "repos/OWNER/REPO".
The optional json-body-file contains the request body as JSON.

Prints the response JSON to stdout. Exits non-zero on HTTP/API errors.
"""

import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (
    add_surrogate_to_request,
    read_json_response,
    DynamicCredentialError,
)

CREDENTIAL = "custom.github"
ALLOWED_HOSTS = ["api.github.com"]
BASE = "https://api.github.com"
API_VERSION = "2022-11-28"


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    method, path = argv[1].upper(), argv[2].lstrip("/")
    url = f"{BASE}/{path}"

    body = None
    if len(argv) > 3:
        with open(argv[3], "r", encoding="utf-8") as f:
            body = json.dumps(json.load(f)).encode("utf-8")

    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "muse-github-skill/1.0")
    req.add_header("X-GitHub-Api-Version", API_VERSION)
    if body is not None:
        req.add_header("Content-Type", "application/json")

    try:
        add_surrogate_to_request(
            req, CREDENTIAL, allowed_hosts=ALLOWED_HOSTS
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(json.dumps(read_json_response(resp), indent=2, ensure_ascii=False))
    except DynamicCredentialError as exc:
        print(f"credential error: {exc}", file=sys.stderr)
        return 3
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8", errors="replace"))
            print(json.dumps(detail, indent=2, ensure_ascii=False), file=sys.stderr)
        except Exception:
            print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
