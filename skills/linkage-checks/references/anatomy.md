# Check anatomy

The 7 structural elements every linkage check script carries. The scaffold
template (`assets/check-template.sh`) implements all of them; keep them when
hand-writing.

1. **Bash wrapper** — `#!/usr/bin/env bash` + `set -euo pipefail`. No logic
   here beyond path resolution; the real work is embedded Python (better
   regexes, testable parsing).
2. **Repo-root resolution** — `REPO_ROOT` derived from the script's own
   location (`dirname "${BASH_SOURCE[0]}"`), never from cwd. The script must
   work when invoked from anywhere.
3. **Env overrides (test hooks)** — every repo-specific input path comes
   from an environment variable with a sensible default. This is what makes
   the check testable against fixture trees without touching the real repo.
   Document each override in the header comment.
4. **Parse A** — extract the definition set. Fail with exit 2 if *zero*
   definitions parse: a check that silently parses nothing passes vacuously
   and is worse than no check.
5. **Scan B** — collect the reference set. Walk the tree; match the exact
   reference syntax (verified against real code in step 2 of the workflow).
6. **Escape hatch** — a marker (`NO_<X>: <reason>`) in a comment *directly
   attached* to the definition. The reason is required and echoed in the
   PASS report. Scope it tightly: a marker "anywhere in the file" silently
   disables the check (caught in production once — reviewer found it with a
   fixture).
7. **Report + exit codes** — `0` pass (`PASS: <n> ...`), `1` offenders
   (list every offender on stdout), `2` usage/misconfiguration (stderr).
   CI greps the PASS line; humans read the offender list.

## CI wiring
Add one step per script in the repo's CI workflow, in the same job as the
other checks. After wiring, confirm the CI log prints the PASS line on a
real run — "the step exists in YAML" is not evidence.
