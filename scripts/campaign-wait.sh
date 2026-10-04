#!/usr/bin/env python3
"""campaign-wait: đánh thức coordinator khi worker ghi result file.

Thay thế việc trông chờ handoff của runtime (đã chứng minh mất tin:
8/8 progress message events delivered_at=null, 2026-10-03).

Cơ chế: worker "POST" bằng cách ghi file `*-result.md` vào scratch dir
(FILE đã là kênh chính). Script này là "webhook": poll stat rẻ bằng
process thường (không tốn LLM turn), thoát ngay khi có file mới/sửa —
runtime giao kết quả exec về sẽ đánh thức coordinator.

Dùng trong coordinator (background exec):
    campaign-wait.sh <scratch-dir> <timeout-seconds> [--expect f1,f2] [--count N] [--fresh-secs S]

- Hết timeout thoát mã 2 (coordinator tự đọc file rồi arm lại).
- --expect: chỉ wake trên đúng các file này (tránh wake giả do file cũ
  bị chạm); file expected nào đã tồn tại lúc arm VÀ mtime trong
  --fresh-secs (mặc định 300) thì báo NGAY — đóng race "worker viết xong
  trước khi waiter kịp snapshot baseline". Re-dispatch: coordinator xóa/
  đổi tên file cũ trước, hoặc truyền --fresh-secs 0 để tắt.
- --count N: đợi đủ N file distinct mới wake (gom nhiều worker một lần).
  Không truyền --expect thì đếm mọi *-result.md mới/sửa.

Không phải HTTP API: không daemon, không port, không auth — filesystem
chính là API, và wake-up đi qua exec-completion delivery (kênh đang chạy).
"""
import argparse
import os
import sys
import time

POLL_SECS = 3


def snapshot(directory, extra_names=()):
    """{filename: mtime} cho mọi *-result.md trong dir (+ file --expect
    kể cả khi tên không khớp pattern, vd MyInjector-Report.md)."""
    extra = set(extra_names or ())
    snap = {}
    for name in os.listdir(directory):
        if name.endswith("-result.md") or name in extra:
            try:
                snap[name] = os.stat(os.path.join(directory, name)).st_mtime
            except OSError:
                pass
    return snap


def main():
    ap = argparse.ArgumentParser(prog="campaign-wait.sh")
    ap.add_argument("scratch_dir")
    ap.add_argument("timeout", type=int)
    ap.add_argument("--expect", default="",
                    help="comma-separated expected result filenames")
    ap.add_argument("--count", type=int, default=1,
                    help="wake after N distinct new/changed files")
    ap.add_argument("--fresh-secs", type=int, default=300,
                    help="expected file newer than this at arm time = report immediately")
    args = ap.parse_args()

    if not os.path.isdir(args.scratch_dir):
        print(f"ERROR: scratch dir not found: {args.scratch_dir}",
              file=sys.stderr)
        return 3

    expected = [n.strip() for n in args.expect.split(",") if n.strip()]
    want = set(expected) if expected else None  # None = any *-result.md
    need = args.count if not expected else min(args.count, len(expected))

    before = snapshot(args.scratch_dir, want)
    now = time.time()

    # Đóng race dispatch→arm: expected file đã có và còn "tươi" thì báo ngay.
    fresh_cutoff = now - args.fresh_secs if args.fresh_secs > 0 else float("inf")
    immediate = sorted(
        n for n, m in before.items()
        if (want is None or n in want) and m >= fresh_cutoff
    )
    if immediate and len(immediate) >= need:
        for n in immediate:
            print(f"NEW: {n}")
        return 0

    seen = set(immediate)
    deadline = now + args.timeout
    while time.time() < deadline:
        time.sleep(POLL_SECS)
        after = snapshot(args.scratch_dir, want)
        for name, mtime in after.items():
            if want is not None and name not in want:
                continue
            if name not in before or after[name] != before[name]:
                seen.add(name)
        if len(seen) >= need:
            for name in sorted(seen):
                print(f"NEW: {name}")
            return 0
    print(f"TIMEOUT: no new result file (saw {len(seen)}/{need})")
    return 2


if __name__ == "__main__":
    sys.exit(main())
