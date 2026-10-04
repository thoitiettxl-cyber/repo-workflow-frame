#!/usr/bin/env bash
# Đóng dấu staged diff sau khi preflight-edit + review đã duyệt,
# ngay trước git commit. Coordinator chạy bước này trong pipeline.
set -euo pipefail

GIT_DIR="$(git rev-parse --git-dir)"
if git diff --cached --quiet; then
  echo "stamp.sh: không có staged change để đóng dấu" >&2
  exit 1
fi
git diff --cached --no-color | sha256sum | cut -d' ' -f1 | tr -d '\n' \
  > "$GIT_DIR/preflight-stamp"
echo "Đã đóng dấu: $(cat "$GIT_DIR/preflight-stamp")"
