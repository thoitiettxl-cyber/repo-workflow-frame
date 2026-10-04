---
name: "judge"
description: "Make structured micro-decisions through typed judgments (choice/noul/score), oh-my-pi style. Use when a task needs a calibrated yes/no probability, picking one option from a defined set, or scoring along a rubric, and the result must be machine-consumable. Backed by the TypeSafe System One API (Jev) when a key is configured; otherwise the agent answers the same questions directly as a text fallback."
---

# Judge

## Purpose
Turn fuzzy micro-decisions into typed judgments that code can consume: a **noul** (yes/no probability), a **choice** (one option + probability distribution + confidence), or a **score** (probability-weighted position on an ordered rubric). This mirrors oh-my-pi's `Judge` abstraction, whose wire format is TypeSafe's System One API.

Reach for this when the decision is small, structured, and repeated — classification, routing, verification, ranking, gating — not for open-ended reasoning.

## Tooling
The CLI lives at `~/workspace/skills/judge/bin/judge` (Python 3, stdlib only):

```bash
# Ask one or more independent questions over the same state in one call
echo '{"state": "Help! My payouts have been failing for 3 days.",
        "questions": {
          "is_urgent": {"type": "noul",
                        "instructions": "Does this convey urgency?",
                        "criteria": {"true": "Explicitly time-sensitive",
                                     "false": "No urgency expressed"}},
          "department": {"type": "choice",
                         "instructions": "Which team should handle this?",
                         "criteria": {"billing": "Payments, invoicing, refunds",
                                      "technical": "Bugs, outages, integrations",
                                      "sales": "Pricing, upgrades, new accounts"}},
          "frustration": {"type": "score",
                          "instructions": "How frustrated is the customer?",
                          "criteria": ["Calm", "Frustrated", "Very angry"]}}}' \
  | ~/workspace/skills/judge/bin/judge
```

Useful flags: `--file request.json` to read the request from a file, `--validate` to check the request shape without calling the API, `--no-cache` to bypass the answer cache.

**Answer cache** (mirrors oh-my-pi's `judgment/cache.ts`): answers are cached per question in SQLite at `~/.cache/judge/judgments.db` (`JUDGE_CACHE_DB` overrides), keyed by sha256 of the canonical state plus model plus the full question definition. A later request re-asking any question about an identical state is answered locally for free; only unanswered questions reach the provider. The response carries a `cached` list of question ids served from cache and zeroed `usage` when nothing was billed. Cache failures only warn on stderr and never break a judgment.

Design questions the way the [typesafe-ai skill](~/workspace/skills/typesafe-ai/SKILL.md) prescribes: one narrow judgment per question, complete meaning in `instructions` (question ids are for code, never sent to the model), named JSON fields in `state` when context has several parts, and a no-match outcome when nothing may fit.

## Auth
The native backend authenticates in this order:

1. `TYPESAFE_API_KEY` env var (explicit override).
2. The vault-stored `custom.typesafe` connector credential (surrogate Bearer header, applied by the CLI itself) — this is the normal path; the key lives in the Secure Vault and is never visible in chat, files, or logs.

Optional: `TYPESAFE_BASE_URL` (default `https://api.typesafe.ai`), `TYPESAFE_DEFAULT_MODEL` (default `jev-latest`).

**No credential, no problem.** Without any credential the CLI exits with a clear error instead of calling the API — that is the signal to do the judgment yourself: read the questions and answer each one directly in the same typed shape (`noul`/`choice`/`score` with probabilities and confidence), as oh-my-pi's `TextJudge` does. Never ask the user to paste a key in chat; if the stored credential is rejected (401), offer to reconnect it rather than handling the raw value.

## Operating Rules
1. Batch independent questions over the same state into one call; they are evaluated in parallel.
2. Ask a second, separate question only when an earlier answer changes what evidence to fetch or which options exist.
3. Treat `confidence` as distribution concentration, not permission to act: low confidence on a harmless preference choice is fine; a `noul` near 0.5 means genuine ambiguity, escalate or gather evidence.
4. Keep policy in code, not in the question: thresholds, weights, and escalation rules live with the caller; the judgment stays a reusable typed signal.
5. Validate with `--validate` before wiring a new question set into a script or scheduled job.
6. Never put secrets (API keys, tokens, passwords, private key material) into
   a judged `state` — the judgment never needs the raw value. Redact or
   summarize code containing secrets before sending (cf. review-loop's
   secret-scan.sh pattern).
