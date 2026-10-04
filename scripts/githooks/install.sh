#!/usr/bin/env bash
# Cài pre-commit hook vào .git/hooks của clone này (copy file, không symlink).
# Chạy 1 lần mỗi clone: ./scripts/githooks/install.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SRC="$REPO_ROOT/scripts/githooks/pre-commit"
HOOK_DIR="$REPO_ROOT/.git/hooks"

cp "$SRC" "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"
if [ ! -f "$REPO_ROOT/.git/githooks-mode" ]; then
  echo "warn" > "$REPO_ROOT/.git/githooks-mode"
fi
echo "Đã cài pre-commit hook (mode=$(cat "$REPO_ROOT/.git/githooks-mode"))"
