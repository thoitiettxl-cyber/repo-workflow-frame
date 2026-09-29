#!/usr/bin/env bash
# Dựng khung repo-workflow-frame vào một repo có sẵn.
# Cách dùng: ./install.sh /đường/dẫn/tới/repo
# Idempotent: chạy nhiều lần không tạo trùng lặp.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Dùng: $0 /đường/dẫn/tới/repo" >&2
  exit 1
fi

DEST="$1"
if [ ! -d "$DEST" ]; then
  echo "Không tìm thấy thư mục: $DEST" >&2
  exit 1
fi

# Thư mục chứa script này = root của repo-workflow-frame
SRC="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Tạo cây thư mục docs
mkdir -p "$DEST/docs/plans/active" \
         "$DEST/docs/plans/completed" \
         "$DEST/docs/decisions" \
         "$DEST/docs/templates" \
         "$DEST/docs/patterns"

# 2. Copy các mẫu (không ghi đè file người dùng đã tùy biến)
copy_if_absent() {
  local src="$1" dst="$2"
  if [ -f "$dst" ]; then
    echo "giữ nguyên (đã có): $dst"
  else
    cp "$src" "$dst"
    echo "đã tạo: $dst"
  fi
}

copy_if_absent "$SRC/docs/README.md"                  "$DEST/docs/README.md"
copy_if_absent "$SRC/docs/WORKFLOW.md"                "$DEST/docs/WORKFLOW.md"
copy_if_absent "$SRC/docs/plans/README.md"           "$DEST/docs/plans/README.md"
copy_if_absent "$SRC/docs/plans/active/README.md"    "$DEST/docs/plans/active/README.md"
copy_if_absent "$SRC/docs/plans/completed/README.md" "$DEST/docs/plans/completed/README.md"
copy_if_absent "$SRC/docs/decisions/README.md"       "$DEST/docs/decisions/README.md"
copy_if_absent "$SRC/docs/templates/exec-plan.md"    "$DEST/docs/templates/exec-plan.md"
copy_if_absent "$SRC/docs/templates/decision.md"     "$DEST/docs/templates/decision.md"
copy_if_absent "$SRC/docs/patterns/encoding-invariants.md" "$DEST/docs/patterns/encoding-invariants.md"
copy_if_absent "$SRC/docs/pairing-mattpocock.md"     "$DEST/docs/pairing-mattpocock.md"

# 3. AGENTS.md: chưa có thì tạo từ mẫu; có rồi thì prepend khối HARNESS
HARNESS_BEGIN="<!-- HARNESS:BEGIN -->"
extract_harness_block() {
  awk "/$HARNESS_BEGIN/{flag=1} flag{print} /HARNESS:END/{if(flag) exit}" "$SRC/AGENTS.md"
}

if [ ! -f "$DEST/AGENTS.md" ]; then
  cp "$SRC/AGENTS.md" "$DEST/AGENTS.md"
  echo "đã tạo: $DEST/AGENTS.md (từ mẫu)"
elif grep -q "$HARNESS_BEGIN" "$DEST/AGENTS.md"; then
  echo "giữ nguyên (đã có khối HARNESS): $DEST/AGENTS.md"
else
  tmp="$(mktemp)"
  extract_harness_block > "$tmp"
  printf '\n' >> "$tmp"
  cat "$DEST/AGENTS.md" >> "$tmp"
  mv "$tmp" "$DEST/AGENTS.md"
  echo "đã prepend khối HARNESS: $DEST/AGENTS.md (nội dung cũ giữ nguyên)"
fi

echo "Xong. Điền các placeholder [ĐIỀN] trong docs/WORKFLOW.md và AGENTS.md cho repo của bạn."
