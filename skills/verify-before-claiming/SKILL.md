---
name: verify-before-claiming
description: Use whenever a response would make a factual claim about an external tool, library, product, repository, or its current feature set — especially when comparing two systems, evaluating whether a project has "ported" or "matched" another, or reacting to a report of work someone (or some other AI agent) claims to have completed. Push hard to trigger this when the user references a specific named project/repo, asks to learn from or port behavior from one system into another, pastes a changelog/commit summary/agent report and asks for a reaction, or asks "is this true / does this actually work / is this really the same as X." Do not rely on memory alone for claims about current feature support, API shapes, or "what X does" — verify against a live source first.
---

# Verify Before Claiming

## Why this exists

Confident-sounding claims about software are cheap to produce and expensive to be wrong about. The person reading the answer will often act on it directly — write a spec, hand it to a coding agent, or decide something is "done." If the claim turns out to be stale, half-remembered, or simply taken at face value from someone else's report, that mistake propagates into real work. The fix is cheap: check the primary source before asserting anything about current state, and be explicit about what was actually checked versus what's still an assumption.

## The core loop

1. **Spot the claims that need checking.** Before answering, scan the request (and your own draft answer) for statements about current behavior: "X supports Y," "X doesn't have Z," "X works the same as W." Timeless facts don't need this (a language's syntax, a well-known historical fact). Anything about a project's *current* feature set, API surface, or behavior does — software changes constantly and memory goes stale fast.

2. **Go to the primary source first.** Prefer the project's own repo/README/docs over blog posts, aggregator summaries, or your own recollection. If the first fetch is thin or doesn't answer the specific question, don't stop — reformulate the search with a more specific angle (a subpage, a docs site, a code-search style query, a different phrasing) and try again. A single shallow search that "sort of" answers the question is not enough when the person will build on the answer.

3. **Separate confirmed from assumed, out loud.** When you report findings, mark clearly which parts came from a source you actually read versus which parts you're inferring or can't check (e.g., "I can't see your actual repo, so I can't verify this number — here's what I'd want you to check yourself"). Don't let confident phrasing imply verification that didn't happen.

4. **Don't take self-reported results at face value.** If someone shares a report of work supposedly completed (a changelog, a commit message, an agent's summary of what it did, test/coverage numbers), treat the specific claims as things to sanity-check, not facts. Look for: numbers that don't move much despite a large claimed scope of work (e.g., coverage barely shifting after "8 new routes"), vague phrasing that could be covering a gap, and claims you can verify externally (e.g., against the real upstream project) versus claims that only the author of the report can confirm. Say plainly which is which, and suggest the specific follow-up question that would close the gap — don't just accept or reject wholesale.

5. **Tell deliberate decisions apart from accidental gaps.** Before concluding something is "missing," check whether there's a stated reason for the limitation (a security tradeoff, a documented design choice, a "not yet supported by upstream" note). Search for the rationale, not just the absence. Present it as a decision the person may want to weigh in on, rather than assuming it's automatically a defect to fix.

6. **Turn findings into something actionable, not just a report.** Once you know what's confirmed, what's assumed, and what's a deliberate tradeoff, structure the answer so the person can act on it immediately — a short comparison (what exists vs. what doesn't, ranked by real-world impact rather than by the order the person listed things), or a concrete next step (a question to ask, a prompt to hand to an agent, a decision to confirm). Don't stop at "here's what I found" if the natural next step is obvious.

## Signals this pattern applies

- The person names a specific project/repo and asks you to compare it to something else, or to make their thing "match" it.
- The person pastes output from another AI agent, a changelog, or a status update and wants your reaction.
- The person asks something phrased as a yes/no about current state ("does it support X," "is this actually the same," "did they really fix this") — these deserve a checked answer, not a remembered one.
- You notice you're about to write "X doesn't support Y" or "X supports Y" without having looked anything up in this turn.

## What good output looks like

- A short table or list separating "confirmed (source: ...)" from "not verifiable from here — ask/check yourself."
- Specific follow-up questions aimed at the exact claim that's shakiest, not a generic "let me know if you have questions."
- Willingness to say "this might be a deliberate tradeoff, not a bug — here's the likely reason" instead of reflexively treating every gap as something to fix.
- No invented specifics (fake version numbers, fake API paths, fake stats) to fill a gap in what was actually found.
