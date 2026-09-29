# Mã hóa invariant

Pattern cho việc thuộc ranh giới kiến trúc, reliability, security hoặc
quality — ví dụ: "mọi secret nằm trong secret store, không vào git",
"mọi tool/endpoint mới phải đăng ký đúng group và fail-closed".

## Quy trình

1. **Tìm thẩm quyền**: một tài liệu/quyết định đã được chấp nhận trong repo
   nêu rõ ranh giới đó. Convention ngầm, pattern code, hay sở thích không
   ghi thành văn **không** phải policy — thiếu thẩm quyền hoặc mơ hồ đáng
   kể thì dừng.
2. **Dùng đúng chủ validation của repo**: thêm check cơ học nhỏ nhất bao phủ
   đúng phạm vi (script verify, test, hoặc bước CI), báo lỗi nêu rõ: vi phạm
   gì, rule nào, hành động tiếp theo là gì.
3. **Proof hai chiều**: hành vi cho phép phải pass (proof dương), hành vi
   bị cấm phải fail **đúng lý do** đã định (proof âm).

## Báo cáo enforcement chính xác

- Check local chạy được hay đã pass: nêu rõ.
- CI có gọi check đó hay không: nêu rõ — chỉ vì check tồn tại trong source
  không có nghĩa là merge bị chặn.

Không tự ý đổi CI, hook hay branch protection khi chưa được duyệt riêng.
