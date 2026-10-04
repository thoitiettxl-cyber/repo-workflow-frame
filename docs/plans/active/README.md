# Active Execution Plans

Đặt một plan đang tiến triển ở đây khi việc cần nhớ bền vững (qua session,
nhiều bước phụ thuộc, cần recovery). Dùng `docs/templates/exec-plan.md`,
giữ tiến độ và validation luôn hiện tại, chỉ move sang `../completed/` sau
khi kết quả đã được verify.

## Campaign-plan (chiến dịch subagent)

Chiến dịch multi-agent là một loại plan hạng nhất — mở trong repo, không chạy
ngoài harness. Layout (`docs/plans/active/<slug>/`):

- `PLAN.md` — outcome, danh sách batch, nhật ký tiến độ, quyết định
  (theo `docs/templates/exec-plan.md`).
- `brief/BRIEF.md` — coordinator brief đã điền
  (copy từ `docs/templates/coordinator-brief.md`).
- `batches/` — `<batch>-<role>-result.md`, `<batch>-fable-check.md`
  (khi có finding). Audit trail → commit vào repo.
- `scratch/` — file transient (edit-script, log nháp); gitignored, không commit.
- `REPORT.md` — viết khi xong; rồi move cả thư mục sang `../completed/`.

Mở campaign-plan TRƯỚC KHI dispatch worker đầu tiên. Ngoại lệ duy nhất:
việc cross-repo/meta mới dùng `~/workspace/workflow-runs/`.
