# Ghép skill vào workflow (harness)

Nguyên tắc: **workflow làm trung tâm, skill là vệ tinh phụ trợ**.
Skill không override "Quy tắc bắt buộc" của repo. "LOẠI khỏi harness" nghĩa là
không nằm trong bộ ghép — skill vẫn giữ nguyên trong kho, không xóa.

Ký hiệu: `*` = cần adapter note (mục Adapter). Không `*` = dùng trực tiếp.

## Bản đồ phase → skill

| Phase | Skill |
|---|---|
| P0 Chọn hình thức việc | technical-scoping-workflow*, to-spec*, wayfinder*, handoff |
| P1 Thẩm quyền (dừng-hỏi) | grilling*, judge*, verify-before-claiming, wizard, to-spec* (seams check = gate P1) |
| P2 Chứng minh hành vi | search-playbook, ai-regression-testing, verify-before-claiming, tdd-workflow*, verification-loop*, eval-harness*, kotlin-testing*, parallel-execution-optimizer |
| P3 Mã hóa invariant | (không skill — frame tự cover qua `docs/patterns/encoding-invariants.md`) |
| P4 Read-only | onboard-repository, diagnosing-bugs*, engineering-wisdom, research*, agent-architecture-audit*, code-review*, librarian, apk-reverse*, binary-diff* |
| P5 Bounded change | commit, git-workflow*, implement*, resolving-merge-conflicts*, tdd-workflow* |
| P6 Plan change | implement*, to-spec*, to-tickets*, wayfinder*, commit, handoff, technical-scoping-workflow* |
| P7 Chuẩn hoàn tất | agent-self-evaluation, update-changelog, verification-loop*, eval-harness*, yeet |
| PX Domain/tool | mcp, documentation-lookup, summarize, uv, ghidra, mcp-builder, golang-patterns, kotlin-patterns, cloudflare, wrangler, workers-best-practices, typesafe-ai, context-budget*, android-clean-architecture, api-design, compose-multiplatform-patterns, error-handling, writing-for-agents, github, reverse-engineering* (playbook tham khảo, không chạy script) |

## Adapter (vênh đã biết → cách xử lý)

**Output về đúng nhà của frame:**
- research: findings ghi vào plan file (Ngữ cảnh) hoặc `docs/plans/active/<slug>.research.md` — không tự tạo `docs/research/` ngoài frame.
- eval-harness: eval artifact đặt trong plan dir, không phải `.claude/evals/`.
- to-spec: repo tắt issues thì plan trong `docs/plans/active/` chính là bản publish; "Do NOT interview" không áp dụng cho chỗ chưa chốt — để Open questions, không bịa (P1).
- wayfinder: dùng local-markdown mode — map là 1 file trong `docs/plans/active/`, decision tickets là sections; ticket HITL chỉ chạy live, chạy nền thì bỏ qua.

**Gate P1 của frame override skill:**
- apk-reverse / binary-diff: khối "ACTION REQUIRED — đọc xong thực thi ngay" bị gate P1 override — vẫn dừng hỏi trước khi chạy.
- grilling: gate tương tác — chỉ chạy khi có user live; chạy nền thì bỏ qua, không kẹt.
- git-workflow: tag/release theo quán tính "flow end-to-end" phải qua gate P1, hỏi Boss trước.
- implement: "commit your work" theo gate của repo — repo không cho auto-commit thì giữ trong plan.
- resolving-merge-conflicts: rule "never `--abort`" nhường P1 — hunk mơ hồ vật chất thì dừng hỏi, ghi trade-off vào plan/ADR trước commit.

**Verify theo repo, không theo mẫu của skill:**
- tdd-workflow: Step 0 detect runner không biết Gradle — map tay sang lệnh verify của repo; evidence report vào plan (Validation/Kết quả), không phải `docs/releases/` hay `.github/tdd/`.
- verification-loop: thay lệnh mẫu npm-centric bằng lệnh verify của repo (mục [ĐIỀN] trong WORKFLOW.md); report gắn vào plan hoặc báo P7.
- kotlin-testing: gate coverage 80% cứng vs frame "proof phù hợp" — lấy min, ghi vào plan.
- ai-regression-testing: ví dụ JS-centric, map runner theo repo.

**Ghi decision có type:**
- judge: mục "Quyết định" của exec-plan có format `choice + confidence`
  cho typed output — không mất dữ liệu từ judge.

**Merge spec/ticket vào plan:**
- to-tickets: tickets là section trong cùng plan file; chỉ externalize ra tracker/file riêng khi repo dùng tracker thật và Boss duyệt.
- technical-scoping-workflow: scoping deliverable merge vào exec-plan theo bảng "Ghép spec của skill vào exec-plan".
- code-review: tìm spec source ưu tiên `docs/plans/active/` trước issue tracker.

**Môi trường Pi:**
- context-budget: map path Claude Code (agents/, .mcp.json, CLAUDE.md) sang môi trường Pi (`~/workspace/skills/`, `~/.config/mcp/mcp.json`).
- handoff: luôn link tới plan đang active ở `docs/plans/active/`, không duplicate nội dung.

## Loại khỏi harness

- **triage**: toàn bộ skill sống trên issue tracker ngoài (đăng comment AI-disclaimer,
  đóng issue), tự hành động trên hệ ngoài không qua gate P1. Giữ trong kho cho
  repo có dùng tracker; đưa lại vào harness nếu frame hỗ trợ tracker.

## Hợp nhất

1. **search-first → search-playbook**: một discipline duy nhất "tra cứu trước khi
   hành động" (playbook thêm nhánh tìm giải pháp có sẵn: adopt/extend/build).
2. **kotlin-coroutines-flows → kotlin-patterns**: trùng section Coroutines/Flow —
   giữ một skill Kotlin trong harness.
3. **architecture-decision-records + domain-modeling → frame** (đã gộp
   2026-09-30): format Nygard + lifecycle + detection signals + "ADR tốt" và
   3 tiêu chí "khi nào ADR" + discipline challenge-terms/glossary đã vào
   `docs/templates/decision.md`; glossary vào plan file — không giữ 2 chuẩn
   ADR song song (docs/adr/ vs docs/decisions/).

## Ghép spec của skill vào exec-plan của khung

Template spec của skill (Problem/Solution/User Stories/Implementation
Decisions/Testing Decisions/Out of Scope/Further Notes) merge vào exec-plan
(`docs/templates/exec-plan.md`) như sau:

| Spec (skill) | Exec-plan (khung) |
|---|---|
| Problem Statement + Solution | Outcome (+ User stories rút gọn) |
| User Stories | Outcome (rút gọn) / Phạm vi |
| Implementation Decisions | Cách làm + Quyết định |
| Testing Decisions | Validation |
| Out of Scope | Phạm vi → Ngoài phạm vi |
| Further Notes | Ngữ cảnh |

Lưu ý:

- Repo tắt Issues: bỏ qua bước "publish ra issue tracker" của skill —
  file plan trong `docs/plans/active/` chính là bản publish.
- Skill bảo "respect ADRs": đọc `docs/decisions/` trước khi viết spec.

## Nguyên tắc ghép

1. Skill quyết định **cách làm**; khung quyết định **output nằm ở đâu** và
   **chuẩn hoàn tất** (bằng chứng chạy được, không phải lời báo).
2. Quyết định lasting nảy sinh trong lúc dùng skill → promote thành ADR trong
   `docs/decisions/`, không để chôn trong chat.
3. Skill không thay thế ranh giới cấm của repo (`AGENTS.md` mục "Quy tắc bắt
   buộc") — ví dụ skill không cho phép tự tạo tag/release hay chạm production
   nếu repo cấm.
