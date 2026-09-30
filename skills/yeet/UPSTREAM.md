# Upstream provenance

This Pi skill was adapted from OpenAI's Apache-2.0 licensed curated `yeet`
skill:

- Source directory:
  https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/yeet
- Pinned commit:
  `49f948faa9258a0c61caceaf225e179651397431`

## Local adaptation

- Preserved the explicit stage, commit, push, and GitHub draft-PR workflow.
- Added Pi repository-instruction and `commit` skill requirements.
- Added checks for unrelated work, generated files, and secret material.
- Replaced unconditional `git add -A` with an authorization and diff gate.
- Removed automatic dependency installation.
- Removed automatic pull/retry behavior after push failures.
- Prohibited implicit force-push, history rewriting, and PR merge.
- Preserved PR-template discovery and existing PR body content.
- Removed `agents/openai.yaml` and decorative assets because Pi does not consume
  them for skill discovery or execution.

## Updating

Before refreshing, compare the pinned source with the latest upstream skill,
review every workflow change for Git and external-mutation safety, preserve the
Pi-specific boundaries above, update the pinned commit, and rerun Pi skill
validation.
