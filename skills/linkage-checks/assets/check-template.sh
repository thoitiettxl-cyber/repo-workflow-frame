#!/usr/bin/env bash
# FILL: <check-name> — <one-line: everything defined at A must appear at B>
#
# FILL: longer description of the invariant, both directions if applicable,
# and what breaks at runtime when it drifts.
#
# A <marked> definition is exempted: the deliberate escape hatch; the reason
# is required and is echoed in the PASS report. There are no such exemptions
# in the tree today.  (FILL: adjust marker name/scope to the pair.)
#
# Test hooks (environment overrides; defaults shown):
#   FILL: FOO_FILE — ...
#   FILL: BAR_DIR  — ...

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# FILL: resolve A/B locations from env overrides with REPO_ROOT defaults, e.g.:
# A_FILE="${A_FILE:-$REPO_ROOT/path/to/definitions}"
# B_DIR="${B_DIR:-$REPO_ROOT/path/to/usages}"

# FILL: fail fast (exit 2) when A/B inputs are missing.

export A_FILE B_DIR

python3 - <<'PYEOF'
import os
import re
import sys

a_file = os.environ["A_FILE"]
b_dir = os.environ["B_DIR"]

src = open(a_file, encoding="utf-8").read()

# --- FILL: parse definitions at site A.
# Produce: defs = [{"name": ..., "exempt_reason": ...|None}, ...]
# Keep the escape-hatch scope TIGHT: the marker must live in the comment
# block directly attached to the definition (not "anywhere in the file"),
# otherwise the hatch silently disables the check.
defs = []
# FILL: your regex / parsing here.

if not defs:
    print("FAIL: no definitions parsed at site A", file=sys.stderr)
    sys.exit(2)

# --- FILL: scan site B for references.
# Produce: refs = set(names referenced at B)
refs = set()
# FILL: walk B_DIR, collect references with your regex.

# --- Compare.
offenders = []
exempted = []
for d in defs:
    name = d["name"]
    if name in refs:
        continue
    if d["exempt_reason"]:
        exempted.append((name, d["exempt_reason"]))
        continue
    offenders.append(name)

# --- Report.
if offenders:
    print("FAIL: %d %s without %s:" % (len(offenders), "FILL:things", "FILL:where"))
    for o in sorted(offenders):
        print("  - %s" % o)
    sys.exit(1)

print("PASS: %d %s ...; %d marked %s, 0 offenders"
      % (len(defs), "FILL:things", len(exempted), "FILL:MARKER"))
for name, reason in sorted(exempted):
    print("  exempt: %s (%s)" % (name, reason))
PYEOF
