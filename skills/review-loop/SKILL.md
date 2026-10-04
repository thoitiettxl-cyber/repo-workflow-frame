---
name: review-loop
description: "Bounded review-fix loop for subagent campaigns, ported from mitsuhiko/agent-stuff review.ts: shared review rubric (P0-P3, fail-fast error handling), per-repo REVIEW_GUIDELINES.md convention, machine-checkable verdict, fix-queue protocol, and structured reviewer handoff. Use after preflight-edit apply, before commit."
---

# Review Loop Skill

A bounded review → fix → re-review loop for coordinator-run campaigns.
Ported from `review.ts` in mitsuhiko/agent-stuff (review rubric adapted from
Codex's review prompt, per-project guidelines file, verdict parsing, loop
with safety cap). The TUI/session-branching parts are not ported — fresh-eyes
subagents replace them, per the SpoofX orchestration pattern.

It sits **after** `preflight-edit` (which blocks mechanical edit errors) and
**before** commit: this loop blocks logic/quality defects.

## 1. General review rubric

Give this rubric to every reviewer subagent (it is the default; a repo's
`REVIEW_GUIDELINES.md` overrides it where they conflict).

```
You are acting as a code reviewer for a proposed code change made by another
engineer. The repo's REVIEW_GUIDELINES.md / REVIEW.md (if provided below)
overrides these general instructions where they conflict.

## Determining what to flag
Flag issues that:
1. Meaningfully impact the accuracy, performance, security, or
   maintainability of the code.
2. Are discrete and actionable (not general issues or multiple combined issues).
3. Don't demand rigor inconsistent with the rest of the codebase.
4. Were introduced in the changes being reviewed (not pre-existing bugs).
5. The author would likely fix if aware of them.
6. Don't rely on unstated assumptions about the codebase or author's intent.
7. Have provable impact on other parts of the code — speculation is not enough.
8. Are clearly not intentional changes by the author.
9. Be particularly careful with untrusted user input (see below).
10. Treat silent local error recovery (especially parsing/IO/network
    fallbacks) as high-signal review candidates unless there is explicit
    boundary-level justification.

## API / framework verification
1. Any API, method, class, or behavior the reviewer is not certain exists in
   the target SDK/framework version must be verified against a primary
   source (source-jar, official docs, Context7) — never taken on trust from
   the writer or from training memory. A wrong-but-plausible API call that
   compiles in the reviewer's head is still a build break.
   (Lesson 2026-10-02: writer called `LocaleList.getEmpty()`, which does not
   exist in the Android SDK; reviewer APPROVEd without checking; CI caught it.)
2. When uncertain about a compile-relevant claim, say so explicitly in the
   handoff rather than approving silently.

## Untrusted user input
1. Open redirects must only go to trusted domains.
2. Always flag SQL that is not parametrized.
3. HTTP fetches of user-supplied URLs must be protected against access to
   local resources (SSRF / DNS interception).
4. Escape, don't sanitize, when you have the option (e.g. HTML escaping).

## Secrets (deterministic checklist)
Secrets must never enter a diff. On every review:
1. Run `scripts/secret-scan.sh` on the batch diff (from the skill dir); triage
   every hit manually — it is a heuristic net, not proof.
2. Also flag by eye: hardcoded API keys/tokens/passwords/private keys in added
   lines, credentials in URLs, secrets in test fixtures that mirror production
   shape.
3. A hit is [P0] if the secret looks real and the branch is shared; [P2] if
   clearly a placeholder/dummy with no production value.
4. Never paste a suspected real secret into chat, logs, or handoffs — refer
   to it by file:line and pattern type only (the script masks values).

## Fail-fast error handling (strict)
When reviewing added or modified error handling, default to fail-fast:
1. Evaluate every new/changed try/catch: what can fail, and why is local
   handling correct at exactly this layer?
2. Prefer propagation over local recovery. If the scope cannot fully recover
   while preserving correctness, rethrow (optionally with context).
3. Flag catch blocks that hide failure signals: returning null/[]/false,
   swallowing parse failures, logging-and-continue, "best effort" silent
   recovery.
4. Parsing/decoding must fail loudly by default; quiet fallbacks only with an
   explicit compatibility requirement and tested behavior.
5. Boundary handlers (routes, CLI entrypoints, supervisors) may translate
   errors but must not pretend success or silently degrade.
6. When uncertain, prefer crashing fast over silent degradation.

## Priorities
Tag each finding: [P0] drop everything, blocking · [P1] urgent, next cycle ·
[P2] normal, eventually · [P3] nice to have.

## Named anti-patterns (flag by name)
1. **Test theater**: tests that assert what the code *already does* instead of
   what it *should do* — tautological assertions, tests mirroring buggy
   behavior, coverage without verification. [P1/P2]
2. **Laundering own output**: treating self-verification as evidence — "I
   checked, it works" with no artifact. A claim is not evidence; demand the
   artifact (test output, log, SHA). Fable-check enforces this at batch level;
   the reviewer enforces it per finding.
3. **Review-as-signature**: silent approval with no demonstrated examination.
   A `correct` verdict must be earned — the handoff's Review Scope (§5) must
   show what was actually examined.

## Risk-scaled bar
Match review intensity to the diff's risk — not every batch deserves the same
depth:
- **High bar** (deep, adversarial): touches IPC/broadcast, security/auth,
  persistence, concurrency, crypto, money, migrations. Assume breakage; hunt.
- **Normal bar**: feature logic, UI, refactors with tests.
- **Light bar** (fast pass): comment/doc-only, renames, dead-code deletion,
  mechanical changes. Don't burn turns; still run secret-scan.
The coordinator states the bar in the batch contract; the reviewer may raise
it (never lower it) with a one-line reason.

## Comment guidelines
Be clear why it is a problem; communicate severity without exaggeration;
be brief (one paragraph); snippets under 3 lines; matter-of-fact tone;
state the scenario/environment where the issue arises.

## Finding anchoring (chống position drift)
Every finding MUST anchor to the exact code it describes:
1. Quote the `existing_code` snippet (≤5 lines, verbatim from the diff) the
   finding is about, with file:line.
2. A finding whose quoted code doesn't match the diff is invalid — re-verify
   or drop it; never "approximate" the location.
3. The handoff format (§5) carries the quote per finding.

## Output rules
1. List EVERY qualifying finding — don't stop at the first one.
2. Order findings severity-first: P0 → P1 → P2 → P3 (critical first, nitpicks
   last). The Fix Queue follows the same order.
3. Only flag code inside the reviewed diff — never pre-existing code outside it.
4. Keep line references short (subranges, not whole files).
5. Ignore trivial style unless it obscures meaning or violates a documented standard.
6. Do not write the fix — only flag issues (short suggestion blocks allowed).
7. End with the verdict section and the human callouts below.

## Verdict
End with exactly:
## Verdict
correct | needs attention
("needs attention" = blocking findings remain.)

## Human Reviewer Callouts (Non-Blocking)
Informational only; they never change the verdict. Include only what applies:
- **This change adds a database migration:** <files/details>
- **This change introduces a new dependency:** <package(s)/details>
- **This change changes a dependency (or the lockfile):** <files/package(s)/details>
- **This change modifies auth/permission behavior:** <what/where>
- **This change introduces backwards-incompatible public schema/API/contract changes:** <what/where>
- **This change includes irreversible or destructive operations:** <operation/scope>
If none apply, write "- (none)".
```

## 2. Per-repo guidelines convention

- Look for `REVIEW_GUIDELINES.md` at the repo root, falling back to
  `REVIEW.md`. Search upward from the working directory to the repo root.
- Paste its full content into the reviewer brief **after** the general
  rubric, with the note: "The following project guidelines override the
  general rubric where they conflict."
- If neither file exists, review with the general rubric only.
- When a review surfaces a *recurring, repo-specific* defect class, propose
  adding it to the repo's file (same nếp as bug-patterns: đụng repo nào thì
  viết cho repo đó). Creating the file itself needs no approval; changing a
  repo's existing curated file should be mentioned to the user first.

## 3. Verdict contract (machine-checkable)

- Blocking = any `[P0]`/`[P1]`/`[P2]` finding outside code fences, OR a
  `needs attention` verdict with no tagged findings.
- The coordinator checks this by reading the reviewer's handoff (grep for
  `[P0]`/`[P1]`/`[P2]` and the `## Verdict` section). No CLI in v1.

## 4. Review loop protocol (coordinator)

Run after `preflight-edit apply`, before commit. `MAX_PASSES` defaults to
3 (configurable per campaign).

```
for pass in 1..MAX_PASSES:
    reviewer = spawn FRESH-EYES subagent (different from the writer;
                 different reviewer each pass if possible)
    brief = diff of the applied batch (git diff / commit range)
          + general rubric (§1)
          + repo's REVIEW_GUIDELINES.md / REVIEW.md (§2)
          + verdict contract (§3)
          + "output the handoff format from §5"
    handoff = reviewer.result
    if no blocking findings (§3):
        commit (existing discipline); DONE
    else:
        writer fixes per Fix Queue: P0 → P1 → P2 (P3 if quick and safe);
        for each skipped/invalid item: one-line reason;
        run relevant tests/checks for touched code;
        writer reports: fixed items / deferred+reasons / verification results
        (this is the fix prompt, §6)
after MAX_PASSES with blocking findings left:
    STOP. Report to the user with the unresolved findings. Never loop forever.
```

Rules:
- The reviewer never fixes; the writer never reviews its own batch.
- A finding the writer proves invalid (with evidence, not opinion) is
  dropped with its reason recorded — it must not reappear in the next pass.
- If a pass produces only P3s, the coordinator may commit and file the P3s
  as follow-ups instead of looping.
- **Finding fingerprint (dedup):** every finding carries a fingerprint
  `path:lineStart-lineEnd:rule-slug` (e.g. `ui/Settings.kt:120-124:null-unsafe`).
  Before flagging, the reviewer checks it against the fingerprint registry
  (fixed/dropped from prior passes, kept in PLAN.md or the batch handoff) —
  same fingerprint twice = do not re-flag.
- **Adversarial pass (option, khi finding khó/tranh cãi):** instead of
  re-reviewing from scratch, brief a fresh reviewer with ONE job: actively
  refute each finding from the previous pass (defense attorney for the code).
  A finding refuted with evidence is dropped + reason recorded; a survivor
  keeps its flag with higher confidence. Never use an adversarial pass to
  "find more issues" — it only judges existing findings.

## 5. Reviewer handoff format

```
## Review Scope — what was reviewed (files, diff range)
## Verdict — correct | needs attention
## Findings — per finding: [P0..P3] + short title + path:line +
             quoted existing_code (≤5 lines, verbatim) +
             fingerprint `path:lineStart-lineEnd:rule-slug` +
             why it matters (brief) + what should change (brief, actionable)
## Fix Queue — ordered checklist, highest priority first
## Constraints & Preferences — discovered during review, or "(none)"
## Human Reviewer Callouts (Non-Blocking) — as in §1, or "- (none)"
```

## 6. Fix prompt (for the writer)

```
Use the latest review handoff in this conversation and implement the
findings now.
1. Treat Findings / Fix Queue as a checklist.
2. Fix in priority order: P0, P1, then P2 (include P3 if quick and safe).
3. If a finding is invalid, already fixed, or not possible right now:
   explain why in one line and continue — do not silently skip.
4. "Human Reviewer Callouts (Non-Blocking)" are informational only.
5. Follow fail-fast error handling: no local catch/fallback recovery unless
   this scope is an explicit boundary that can safely translate the failure.
   If you add or keep a try/catch, state the expected failure mode.
6. Run the relevant tests/checks for touched code where practical.
7. End with: fixed items, deferred/skipped items (with reasons), and
   verification results.
```

## 7. Relation to existing pieces

- `preflight-edit` → mechanical gate (anchor/parse/overlap). `review-loop` →
  logic/quality gate. They run in sequence, never merged.
- `code-review` skill → one-shot deep review (Standards × Spec axes) for
  PRs/branches on user request. `review-loop` → the fix loop inside
  campaigns. A campaign coordinator uses `review-loop`; the user asks for
  `code-review` directly.
- Bug-patterns library → the reviewer should also have the domain's
  bug-pattern files in context (existing AGENTS.md rule: read them before
  coding — same for reviewing).
