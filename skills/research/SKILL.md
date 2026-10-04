---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent. Includes the deep-research workflow (sub-questions, multi-source search, adversarial cross-examination, cited report with confidence) and quality rules.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.

## Deep-research workflow

For questions needing 3+ sources, comparisons, technology evaluations, or due
diligence. Adapted from ECC `deep-research` (moved here from `search-playbook`
2026-09-30 so the workflow lives in exactly one place).

1. Understand the goal: ask 1–2 short questions (purpose, angle). If told
   "just do it", use a sensible default — don't interrogate.
2. Split into 3–5 sub-questions.
3. Per sub-question: 2–3 keyword variants, search via 2+ tools
   (`browser.search` + exa `web_search_exa` / firecrawl `firecrawl_search`).
   Target 15–30 unique sources. Prefer: academic / official / reputable press
   over blogs over forums.
4. Deep-read 3–5 key sources via full scrape (`browser.open` /
   `web_fetch_exa` / `firecrawl_scrape`). Never rely on snippets.
5. Write the report: Executive Summary → themes → Key Takeaways → Sources →
   Methodology (queries run, sources read) + confidence (High/Medium/Low).
6. Broad topic → split into parallel subagents, main agent synthesizes.
7. **Adversarial phase** (mandatory for deep research, see below) — never
   publish the report straight from step 6.

### Adversarial phase (đối kháng — bắt buộc)

Proven 2026-10-04 on HMA-OSS research: without it, 4 wrong findings and
mis-cited line numbers would have gone straight to the final report.

1. **Independent survey:** 2 teams research in parallel, neither reads the
   other's work. Each writes its own findings file with file:line (or
   source link) per claim. Claims the team cannot verify get labeled
   `[GUESS]` — honestly, in the open.
2. **Cross-attack:** swap reports. Each team attacks ONLY the evidence:
   which claim lacks a source? which file:line is wrong? which inference
   jumps? Verdict per finding: **SURVIVES** (stands), **REFUTED** (wrong,
   with counter-evidence), **WEAKENED** (core right, detail/label wrong).
   Fair play: findings honestly labeled `[GUESS]` are not attacked —
   only claims stated with confidence.
3. **Synthesis:** the coordinator writes the final REPORT from surviving
   findings only, each with its evidence + verification level. Dropped
   findings are listed with their reason — they must not silently return.

Scale by stakes: full 2-team attack for deep/decision-driving research;
for light research, one researcher + one attacker (lighter pass).

### Quality rules

- Every claim has a source. No unsourced claims.
- Single-source claim → flag as unverified.
- Prefer sources <12 months old.
- Data gap → say so, don't invent.
- Separate fact from inference/estimate.
