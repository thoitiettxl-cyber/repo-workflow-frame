# Workflow làm việc

Theo mẫu repository-harness. Hành vi sản phẩm, kiến trúc, quyết định, plan,
code, test và tín hiệu runtime của repo là nguồn sự thật.

## Bản đồ repo

- `AGENTS.md`: bản đồ入口 và ranh giới thẩm quyền.
- `README.md`, `docs/` (product, architecture, decisions): ý định và ràng buộc
  hiện tại.
- `docs/plans/`: việc bền vững; `docs/templates/`: mẫu plan/ADR.
- Code, test, CI và tín hiệu runtime: sự thật chạy được và quan sát được.

## Chọn hình thức việc

### Việc có cần nhớ bền vững?

Việc bounded, một lần xong → làm trực tiếp, không cần plan.

Tạo một plan trong `docs/plans/active/` (theo `docs/templates/exec-plan.md`)
khi việc kéo dài qua session, có phụ thuộc đáng kể, cần khôi phục, hoặc không
resume an toàn được chỉ từ git diff. Giữ outcome, ngữ cảnh, cách làm, rủi ro,
tiến độ, quyết định và validation trong cùng một file; xong và đã verify thì
move sang `docs/plans/completed/`.

### Việc có cần người quyết?

Trước khi sửa, xác định thẩm quyền cho policy mới quan sát được từ bên ngoài.
Nếu còn lựa chọn khác biệt đáng kể, **dừng và hỏi quyết định nhỏ nhất**.
Không tự bịa policy. Default cấu hình được không phải thẩm quyền.

[ĐIỀN: các ranh giới cấm cụ thể của repo này — ví dụ: không tự tạo tag/release,
không thao tác production/đặc quyền khi chưa duyệt, nguồn verify duy nhất là gì.]

Các trường hợp khác còn mơ hồ (ý định sản phẩm, recovery khó, giảm
validation, security, compatibility) → dừng hỏi.

### Cái gì chứng minh hành vi?

[ĐIỀN: nguồn verify của repo này là gì — ví dụ: CI nào, lệnh test nào, log nào.
Plan, checklist hay lời báo "xong" không thay thế được bằng chứng chạy được.]

Nguyên tắc: đọc log/kết quả trực tiếp, không đoán nguyên nhân. Khi verify đỏ:
đọc đúng dòng báo lỗi, fix đúng chỗ, review lại phần fix rồi mới báo xong.

### Việc có mã hóa invariant?

Với ranh giới kiến trúc / reliability / security / quality
(ví dụ: [ĐIỀN — ví dụ: "mọi API key nằm trong secret store, không vào git",
"mọi tool mới phải đăng ký đúng group và fail-closed"]):

1. Tìm thẩm quyền đã chấp nhận trong repo nêu ranh giới đó. Convention ngầm
   hay sở thích không ghi thành văn **không** phải policy — thiếu thẩm quyền
   thì dừng.
2. Thêm check cơ học nhỏ nhất bao phủ đúng phạm vi, báo lỗi nêu rõ: vi phạm
   gì, rule nào, hành động tiếp theo là gì. Chi tiết ở
   `docs/patterns/encoding-invariants.md`.
3. Cần proof dương (hành vi cho phép pass) và proof âm (hành vi cấm fail đúng
   lý do).

Không tự ý đổi CI, hook hay branch protection khi chưa được duyệt riêng.

## Các luồng việc

### Đọc / review / chẩn đoán (read-only)

Chỉ đọc đúng phần cần cho câu trả lời, review, chẩn đoán, plan hoặc status.
Không sửa file. Phát hiện được gì cũng không mặc nhiên được quyền sửa.

### Thay đổi bounded

Nêu lại outcome → kiểm tra thẩm quyền, implementation, pattern, proof →
sửa nhỏ nhất thành một khối coherent → chạy check liên quan → báo outcome,
thay đổi, bằng chứng và giới hạn. Không cần plan riêng.

### Thay đổi bền vững có plan

Tạo/resume một active plan, triển khai theo nhóm verifiable, promote quyết
định lasting thành ADR trong `docs/decisions/`, chạy proof của repo, ghi kết
quả rồi move plan sang `docs/plans/completed/`.

### Vận hành ứng dụng thật

[ĐIỀN: runbook vận hành của repo này — ai được thao tác ở đâu, agent có được
chạm vào production/thiết bị thật không. Nếu chưa có runbook đã verify thì
ghi rõ, không bịa lệnh.]

## Chuẩn hoàn tất

Một thay đổi được coi là xong khi: outcome tồn tại hoặc blocker đã nêu rõ,
sự thật trong repo còn hiện tại, proof phù hợp đã pass (hoặc gap đã công
khai), plan đã cập nhật, và báo cáo tách bạch facts / limits / việc chưa thử.
Mô tả không thay thế bằng chứng quan sát được.
