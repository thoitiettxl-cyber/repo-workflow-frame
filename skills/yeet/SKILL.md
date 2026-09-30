---
name: yeet
description: "Use only when the user explicitly asks Pi to stage authorized changes, create a Git commit, push the branch, and open or update a GitHub pull request in one end-to-end flow using `git` and `gh`. Do not trigger for requests that ask for only one or some of those actions."
license: Apache-2.0; adapted from OpenAI curated `yeet`—see LICENSE.txt and UPSTREAM.md
compatibility: Requires Git, an authenticated GitHub CLI `gh`, a configured remote, and permission to push and create pull requests.
metadata:
  source: https://github.com/openai/skills
  source-commit: 49f948faa9258a0c61caceaf225e179651397431
  adapted-for: pi
---

# Yeet: Commit, Push, and Open a PR

> Adaptation notice: this Pi skill modifies OpenAI's curated `yeet` workflow.
> It preserves the explicit stage → commit → push → PR intent while adding Pi's
> repository-authority, unrelated-work, credential, validation, and destructive
> Git safety boundaries. Codex-only UI metadata and assets were removed.

Run this workflow only when the user explicitly requests the complete sequence.
A request to inspect, review, plan, commit only, push only, or create a PR only
does not authorize the other steps.

## Preconditions

1. Read repository and nested `AGENTS.md` files and the repository's documented
   workflow and verification commands.
2. Load and follow Pi's `commit` skill before creating the commit.
3. Confirm the required tools and authentication without exposing credentials:
   ```bash
   git --version
   gh --version
   gh auth status
   ```
4. Resolve and report the exact repository, remote, branch, and GitHub target:
   ```bash
   repo_root="$(git rev-parse --show-toplevel)"
   git -C "$repo_root" remote -v
   git -C "$repo_root" branch --show-current
   gh repo view --json nameWithOwner,url,defaultBranchRef
   ```
5. Inspect all tracked and untracked changes with `git status --short` and a
   relevant diff. Do not expose secret file contents while reviewing status.
6. Stop before staging if the worktree contains unrelated user work, generated
   artifacts that should not be committed, credentials, private keys, tokens,
   `.env` secrets, or ambiguous files. Ask the user for the smallest decision.
7. Do not install dependencies or modify system state merely to make this
   workflow pass. Follow repository-owned setup instructions or report the
   missing prerequisite.

## Branch and Naming

- If currently on the repository's default branch, create a short descriptive
  branch using the repository's naming convention. If no convention exists,
  use a lowercase hyphenated slug such as `fix-auth-timeout`.
- If already on a feature branch, remain on it unless the user explicitly asks
  for another branch.
- Never create commits directly on the default branch unless the repository
  explicitly permits it and the user explicitly requested it.
- Use a terse commit subject that describes the net change.
- Format the PR title as `<type>(<scope>): <subject>` when consistent with the
  repository; scope is optional. Typical types are `feat`, `fix`, `docs`,
  `style`, `refactor`, `test`, and `chore`.

## PR Template Discovery

Resolve template paths from the repository root, in this order:

- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- one `*.md` file under `.github/pull_request_template/`
- one `*.md` file under `.github/PULL_REQUEST_TEMPLATE/`

If exactly one template exists, read and preserve its meaningful headings,
required checklists, and repository-specific prompts. If multiple templates
exist and no repository rule selects one, stop before PR creation and ask which
template to use. If none exists, use the fallback body below.

Use repository-relative paths such as `.github/pull_request_template.md`, not
absolute local paths.

## Workflow

### 1. Review and Validate

- Review `git status --short`, staged and unstaged diffs, and relevant untracked
  files.
- Run focused proof and the repository's mandatory validation before committing.
- A skipped required check is not a pass. If validation fails, stop and report
  the failure unless the user explicitly authorizes continuing with a clearly
  documented failing state.

### 2. Stage Authorized Changes

- If the user explicitly authorized all current changes and review confirms
  they are coherent and safe, stage them with:
  ```bash
  git add -A
  ```
- Otherwise stage only the explicitly authorized paths:
  ```bash
  git add -- path/to/file another/path
  ```
- Recheck `git status --short` and `git diff --cached`. Stop if the staged diff
  includes unrelated changes or secret material.

### 3. Commit

Follow the `commit` skill's requirements. Create one coherent commit unless the
repository or user requires a different structure:

```bash
git commit -m "<description>"
```

Record the resulting commit ID and verify the worktree state. Do not amend,
rewrite history, or bypass hooks unless explicitly authorized for the exact
operation.

### 4. Push

Push the current branch with tracking:

```bash
git push -u origin "$(git branch --show-current)"
```

Never force-push. If push fails, diagnose and report the actual authentication,
remote, protection, non-fast-forward, hook, or workflow-permission error. Do not
silently pull, merge, rebase, alter credentials, or retry a materially different
operation without authorization.

### 5. Find or Create the Pull Request

Check whether the current branch already has a PR:

```bash
gh pr view "$(git branch --show-current)" \
  --json number,isDraft,title,body,url
```

- If a PR exists, update that PR rather than creating a duplicate. Preserve its
  ready/draft state and important existing content, especially images, issue
  links, reviewer instructions, and manually maintained checklists.
- If no PR exists, create a new **draft** PR. Use the selected template when one
  exists:
  ```bash
  GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0 \
    gh pr create --draft --fill --template "$template" \
    --head "$(git branch --show-current)"
  ```
- Without a template:
  ```bash
  GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0 \
    gh pr create --draft --fill --head "$(git branch --show-current)"
  ```
- Never merge the PR as part of `yeet`.

### 6. Set the Final PR Title and Body

Describe the net committed diff, not attempts that were later reverted. Explain
why the change is needed before what changed. Do not include absolute local
paths.

Fallback body when no repository template exists:

```markdown
## Why

Describe the user-facing or maintainer-facing problem, including cause and
impact where useful.

## What Changed

Describe the net implementation change concisely.
```

Include a verification section only when it contains reviewer-useful behavioral
evidence or when the repository template requires it. Do not add generic filler
consisting only of routine lint, type-check, formatter, hook, or CI commands.
When a required template section has no evidence, state `Not run` with a reason.

Write the body to a private temporary file with real newlines and pass it through
`--body-file`; remove only that temporary file afterward:

```bash
gh pr edit PR_NUMBER --title "<title>" --body-file "$body_file"
```

## Completion Report

Report:

- repository and branch;
- committed paths and commit ID;
- validation commands and outcomes;
- push result;
- PR number, draft/ready state, and URL;
- any unresolved risk, skipped proof, or external check still pending.

Do not claim completion if commit, push, PR creation/update, or required
validation failed.
