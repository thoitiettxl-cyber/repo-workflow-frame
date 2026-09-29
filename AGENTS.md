# AGENTS.md

<!-- HARNESS:BEGIN -->
## Khung làm việc (harness)

Bắt đầu từ outcome được yêu cầu, lấy repo làm nguồn sự thật. Đọc
`docs/WORKFLOW.md` và chỉ đọc thêm material liên quan (product, design, plan,
code, validation).

- Trả lời, giải thích, review, chẩn đoán, plan, báo status: chỉ đọc, không sửa.
- Thay đổi bounded: kiểm tra behavior + proof liên quan, implement, validate.
- Việc qua session / nhiều bước phụ thuộc / cần recovery: một file plan trong
  `docs/plans/active/`, chỉ move sang `docs/plans/completed/` sau khi kết quả
  đã verify.
- Trước khi sửa: xác định thẩm quyền trong repo cho mỗi policy mới quan sát
  được từ bên ngoài. Còn lựa chọn khác biệt đáng kể → dừng trước khi sửa;
  default cấu hình được không phải thẩm quyền.
- Việc invariant (kiến trúc / reliability / security / quality): đọc
  `docs/patterns/encoding-invariants.md`, chỉ enforce rule đã được chấp nhận.
- Dừng khi: ý định sản phẩm mơ hồ, recovery khó, validation bị yếu đi, hoặc
  thẩm quyền không đủ. Các ranh giới cấm cụ thể của repo này ở mục
  "Quy tắc bắt buộc" bên dưới.
- Báo xong chỉ với bằng chứng chạy được hoặc quan sát được. Báo cáo tách bạch
  outcome, thay đổi, validation và rủi ro chưa giải quyết.
<!-- HARNESS:END -->

## Quy tắc bắt buộc

[ĐIỀN: các ranh giới cấm cụ thể của repo này. Ví dụ:
- Không tự tạo tag / release khi chưa được yêu cầu rõ.
- Không thao tác đặc quyền / production khi chưa được duyệt.
- Không lưu secret (key/token) vào file, memory hay chat log.]

## Lệnh thường dùng

[ĐIỀN: các lệnh verify/build/test chuẩn của repo này.]

## Bài học đã trả giá

[ĐIỀN: các bẫy từng gặp trong repo này — nguyên nhân thật + cách tránh.
Mỗi bài học nên gắn với bằng chứng (log/test), không ghi phỏng đoán.]
