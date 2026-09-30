---
name: technical-scoping-workflow
description: Use when scoping a non-trivial technical effort that requires comparing current and target systems, prioritizing multiple gaps, sequencing dependent work, planning migrations, integrations, or feature-parity work, or producing an execution spec for a teammate or coding agent. Also use when reviewing a progress report to identify remaining gaps and next priorities. Do not use for a single isolated change, a simple explanation, or immediate implementation that does not need a separate scoping deliverable.
---

# Technical Scoping Workflow

Produce an evidence-backed scope that makes priorities, decisions, dependencies,
risks, and completion criteria explicit without prematurely prescribing an
implementation.

## Establish the evidence baseline

1. Inspect the current system's repository, documentation, tests, and observable
   behavior before describing its capabilities.
2. Verify material claims about a reference or target system against current
   primary sources. Record the relevant version or date when behavior may vary.
   Use `$verify-before-claiming` when it is available and applicable.
3. Label each material claim as confirmed, inferred, conflicting, or unknown.
   Do not convert an unverified assumption into a gap.
4. If evidence is insufficient, state what evidence is missing and whether it
   blocks prioritization or can remain an explicit non-blocking assumption.

## Model the gaps

5. Convert vague goals such as "full parity" or "make it professional" into
   discrete, checkable capabilities. For comparison work, use a gap matrix with
   these fields when relevant:

   - capability;
   - current state;
   - target state;
   - evidence and confidence;
   - intentional tradeoff or constraint;
   - user or system impact;
   - dependencies;
   - risk and reversibility;
   - decision or open question;
   - acceptance signal.

6. Check whether each apparent gap is deliberate, such as a security boundary,
   compatibility choice, stability constraint, or upstream limitation. Present
   deliberate differences as decisions, not defects.
7. Exclude capabilities that the evidence does not confirm. Put them under
   "unconfirmed or out of scope" instead of silently inventing parity work.

## Prioritize and sequence

8. Prioritize by user impact, urgency, dependency, uncertainty, blast radius,
   and reversibility rather than by the order in which items were requested.
   State the reason for any meaningful resequencing.
9. Separate uncertainty reduction from production rollout:

   - investigate high-uncertainty or architecture-defining risks early through
     research, prototypes, or reversible spikes;
   - implement in dependency order using the smallest coherent increments;
   - roll out irreversible, credential-sensitive, authentication-sensitive, or
     high-blast-radius changes only after prerequisites and safeguards are proven.

10. Surface material tradeoffs plainly. Obtain an informed user decision before
    scoping work that changes a security boundary, expands authority, creates an
    irreversible migration, or materially changes the requested outcome.

## Define executable work units

11. Decompose the effort into the smallest coherent, independently verifiable
    units. Prefer a complete vertical slice when splitting by component would
    leave untestable or unusable fragments.
12. Require each unit to have an objective, dependencies, constraints,
    deliverables, acceptance evidence, and a rollback or recovery approach when
    failure would have material impact.
13. Require independent toggling only when staged rollout, rollback, operational
    safety, or product control justifies its complexity.

## Write the scoping deliverable

Organize the result around:

1. objective and non-goals;
2. evidence baseline and confidence;
3. gap matrix or explicit capability list;
4. priorities and sequencing rationale;
5. phased work units with dependencies and acceptance evidence;
6. confirmed decisions and constraints;
7. blocking and non-blocking open questions;
8. unconfirmed or out-of-scope items;
9. overall definition of done and required verification.

Resolve decisions supported by available evidence. Preserve genuine open
questions with an owner or decision point instead of presenting them as finished
instructions. Specify implementation details only when they are established
constraints or necessary for interoperability, safety, or acceptance.

## Final quality check

Before delivering the scope, confirm that:

- every claimed gap has evidence or is explicitly marked unverified;
- intentional differences are not mislabeled as missing features;
- priority reflects impact and dependency rather than request order;
- high uncertainty is tested early while high-blast-radius rollout remains gated;
- work units are coherent and independently verifiable;
- security or authority changes await an informed decision;
- every phase has concrete acceptance evidence;
- "done" includes the repository's authoritative verification requirements.
