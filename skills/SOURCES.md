# Nguồn skill trong bundle

56 skill khớp đúng bản đồ phase → skill trong
[`docs/pairing-skills.md`](../docs/pairing-skills.md). Skill **triage** không
bundle (đã loại khỏi harness — xem pairing doc).

Mỗi skill giữ nguyên nội dung như lúc bundle (2026-09-30). License của từng
skill tuân theo collection gốc. File `LICENSE*` nằm trong thư mục skill nào
thì giữ nguyên ở đó.

| Skill | Nguồn | License |
|---|---|---|
| research, code-review, diagnosing-bugs, grilling, grill-with-docs, codebase-design, handoff, implement, resolving-merge-conflicts, to-spec, to-tickets, wayfinder, wizard, writing-for-agents | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT © 2026 Matt Pocock |
| ai-regression-testing, eval-harness, verification-loop, kotlin-testing, kotlin-patterns, android-clean-architecture, api-design, compose-multiplatform-patterns, error-handling, agent-self-evaluation, agent-architecture-audit, context-budget, parallel-execution-optimizer, documentation-lookup, tdd-workflow, git-workflow | [affaan-m/ecc](https://github.com/affaan-m/ecc) | MIT © 2026 Affaan Mustafa |
| uv, update-changelog, summarize, librarian, ghidra, commit, github | [mitsuhiko/agent-stuff](https://github.com/mitsuhiko/agent-stuff) | xem repo gốc |
| judge, mcp, search-playbook, review-loop, preflight-edit, linkage-checks | Pi/Muse tự build | MIT (theo frame) |
| mcp-builder, yeet | Boss (filebin zip, 2026-09-30) | Apache-2.0 (`LICENSE.txt` trong thư mục skill) |
| verify-before-claiming, golang-patterns, technical-scoping-workflow | Boss (filebin zip, 2026-09-30) | không rõ — giữ nguyên nội dung gốc |
| typesafe-ai | [typesafe-ai/skills](https://github.com/typesafe-ai/skills) | MIT |
| cloudflare, workers-best-practices, wrangler | [cloudflare/skills](https://github.com/cloudflare/skills) | Apache-2.0 |
| onboard-repository, engineering-wisdom | [hoangnb24/repository-harness](https://github.com/hoangnb24/repository-harness) | MIT |
| apk-reverse, binary-diff, reverse-engineering | zhaoxuya520 (reverse-skill) | MIT |

## Skill đã adapt so với bản gốc

- `research`: đã merge workflow deep-research 6 bước từ `search-playbook`.
- `search-playbook`: mục deep-research đã tách sang skill `research`.
- `eval-harness`: đã gỡ section trỏ script không tồn tại.
- `mcp`: đã sửa tên server cho khớp config thực tế.
- `kotlin-patterns`: đã gộp nội dung từ `kotlin-coroutines-flows`.

## Không bundle

- Môi trường chạy (`.venv`, `__pycache__`, `node_modules`, cache) — người dùng
  tự dựng theo `SKILL.md` của từng skill.
