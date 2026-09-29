# docs/plans

Kế hoạch cho các việc kéo dài nhiều session, nhiều bước, hoặc cần phối hợp.

## Quy ước

- Việc bounded, làm một lần xong → khỏi ghi plan, làm trực tiếp.
- Việc nào thỏa một trong các điều kiện sau thì tạo plan ở đây:
  - kéo dài qua nhiều session,
  - có nhiều bước phụ thuộc nhau,
  - cần khôi phục (recovery) nếu dở dang,
  - không thể resume an toàn chỉ từ git diff.
- Một việc = một file plan duy nhất, đặt trong `active/`, theo mẫu
  `docs/templates/exec-plan.md`. Tiến độ và quyết định cục bộ ghi chung
  trong file plan, không tách nhiều file song song nếu không có đối tượng đọc
  riêng.
- Việc xong và đã verify → chuyển file sang `completed/`.
