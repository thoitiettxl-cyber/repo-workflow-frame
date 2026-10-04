# Git hooks — "gác cổng" của pipeline preflight+review

## Vấn đề

Quy định "worker không tự sửa file, chỉ nộp edit-script" trước đây chỉ nằm
trong brief (luật viết tay). Worker lén dùng Edit trực tiếp thì phải chờ CI đỏ
mới phát hiện (~10 phút + 1 commit rác).

## Cơ chế

- `pre-commit`: git tự chạy mỗi lần `git commit`. So hash của staged diff với
  "giấy phép" (`.git/preflight-stamp`). Khớp → cho qua; không khớp → tùy mode.
- `stamp.sh`: coordinator chạy sau `git add`, trước `git commit`, để đóng dấu.
- `install.sh`: copy hook vào `.git/hooks` (chạy 1 lần mỗi clone).

## Hai mode (học thuyết thích nghi: smoke test trước, promote sau)

1. `warn` (mặc định): thiếu/sai stamp → chỉ ghi `.git/githooks.log`, vẫn cho
   commit. Dùng để quan sát, không gián đoạn việc đang chạy.
2. `enforcing`: thiếu/sai stamp → chặn commit tại chỗ (exit 1).

Lên `enforcing` khi: pipeline đã chứng minh đóng dấu đúng qua ít nhất 1 chiến
dịch (log toàn `result=stamped`, không false positive).

## Luật

- Stamp là hash của đúng staged diff → single-use theo nội dung: diff khác thì
  dấu cũ không khớp, không tái dùng được.
- Worker KHÔNG BAO GIỜ dùng `git commit --no-verify`. Cờ đó chỉ dành cho
  root/hotfix khẩn cấp.
- File trong `.git/` (mode, stamp, log) không commit vào repo.
