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
  `docs/templates/exec-plan.md`. Tên file: kebab-case `^[a-z0-9-]+\.md$`,
  ví dụ `add-naming-convention-check.md` (không cần số thứ tự như ADR).
- Việc xong và đã verify → đổi `## Trạng thái` thành Completed trong file,
  rồi mới chuyển file sang `completed/`.
