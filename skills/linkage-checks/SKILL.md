---
name: linkage-checks
description: "Turn 'defined in A, must appear in B' invariants into CI check scripts. Use when a repo has definition/usage pairs that drift silently (toggles without UI rows, modules without registry keys, JNI names, i18n keys, routes, permissions). Scaffolds bash+python check scripts with escape hatches, fixture self-tests, and CI wiring."
---

# Linkage Checks

A **linkage** is an invariant of the form: *everything defined at site A must
appear at site B*. When it breaks silently, the bug is invisible until runtime:
a toggle with no UI row, a module with no registry key, a native function
whose Kotlin declaration was renamed, an i18n key with no translation.

This skill turns each linkage into a small CI check script that fails loudly
on drift, so human reviewers stop spending eyes on what a machine can verify.

## Workflow

### 1. Identify pairs
Survey the repo and list candidate A↔B pairs (see `references/pair-catalog.md`
for common ones). Pick pairs where drift is a **real bug**, not trivia. For
each pair, write down:
- **A (definition site)**: file(s), exact syntax of a definition.
- **B (appearance site)**: file(s), exact syntax of a reference.
- **Direction**: A→B (every A must appear in B), B→A, or both.

### 2. Verify the mechanism first
Read both sides before writing any check. Confirm the extraction you plan is
reliable on the real code — not on your memory of how it "should" look.
(Lesson from production: a JNI check written against assumed `Java_*` naming
would have missed every `RegisterNatives` entry. The writer read the
registration code first, then designed the check.)

If extraction is unreliable (dynamic names, string-built keys), **do not**
force the check — document the pair as deferred with reasons.

### 3. Scaffold
```
bin/new-linkage-check <check-name> [--repo DIR]
```
Generates `scripts/checks/<check-name>.sh` from the template plus a fixture
skeleton under `scripts/checks/tests/fixtures/<check-name>/`
(`pass/`, `fail/`, `exempt/`). Fill the `FILL:` sections: parse-A, scan-B,
compare, escape hatch.

### 4. Self-test with fixtures
- **pass/**: faithful miniature of the real tree → script exits 0, prints PASS.
- **fail/**: one synthetic offender → exits non-zero, names the offender.
- **exempt/**: offender carrying the escape-hatch marker → exits 0.
Run all three. A check that cannot demonstrate catching an offender is not
done.

### 5. Wire into CI
Add a step to the repo's CI (same job as the other checks). Confirm the CI
log prints the PASS line on a real run — "the step exists" is not evidence.

## Check anatomy
Every generated script follows the same 7 elements (see
`references/anatomy.md`): bash wrapper, repo-root resolution, env overrides
for testability, embedded Python (parse A / scan B / compare), escape hatch,
PASS/FAIL report, exit codes (`0` pass · `1` offenders · `2` usage/misconfig).

## Output contract
- One script per pair: `scripts/checks/<name>.sh`, executable.
- stdout ends with `PASS: <n> ...` or `FAIL: <offenders...>`; stderr for
  misconfiguration.
- Fixtures live next to the script so the next agent can re-verify.

## Operating rules
1. **Verify, don't guess** the extraction — read both sites first.
2. Every check **must** have an escape hatch (`NO_<X>: <reason>`); the reason
   is required and echoed in the PASS report. An escape hatch with wrong scope
   silently disables the check — the self-test must cover it.
3. Env-var overrides for all repo-specific paths (testability is not optional).
4. One pair per script. A script checking two pairs is two scripts.
5. If a pair proves too noisy, defer it **in writing** with the concrete
   false-positive causes — never ship a check you don't trust.
