#!/usr/bin/env bash
# Dựng khung repo-workflow-frame vào một repo có sẵn.
# Cách dùng: ./install.sh /đường/dẫn/tới/repo [--with-skills|--without-skills] [--skills-dir DIR]
# Idempotent: chạy nhiều lần không tạo trùng lặp.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Dùng: $0 /đường/dẫn/tới/repo [--with-skills|--without-skills] [--skills-dir DIR]" >&2
  exit 1
fi

DEST="$1"; shift
WITH_SKILLS=""
SKILLS_DIR="${HOME}/workspace/skills"
while [ $# -gt 0 ]; do
  case "$1" in
    --with-skills) WITH_SKILLS="yes" ;;
    --without-skills) WITH_SKILLS="no" ;;
    --skills-dir)
      SKILLS_DIR="$2"; shift ;;
    *) echo "Flag lạ: $1" >&2; exit 1 ;;
  esac
  shift
done
if [ ! -d "$DEST" ]; then
  echo "Không tìm thấy thư mục: $DEST" >&2
  exit 1
fi

# Thư mục chứa script này = root của repo-workflow-frame
SRC="$(cd "$(dirname "$0")/.." && pwd)"

# Số skill trong bundle (trừ README.md/SOURCES.md là metadata)
SKILL_COUNT="$(ls "$SRC/skills" | grep -v -x -e README.md -e SOURCES.md | wc -l)"

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
copy_if_absent "$SRC/docs/templates/coordinator-brief.md" "$DEST/docs/templates/coordinator-brief.md"
copy_if_absent "$SRC/docs/patterns/encoding-invariants.md" "$DEST/docs/patterns/encoding-invariants.md"
copy_if_absent "$SRC/docs/pairing-skills.md"          "$DEST/docs/pairing-skills.md"
copy_if_absent "$SRC/LICENSE"                        "$DEST/LICENSE"

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

# Cảnh báo nếu docs/ bị .gitignore nuốt: plan/ADR sẽ chỉ nằm local, không vào git.
if [ -d "$DEST/.git" ] && git -C "$DEST" check-ignore -q docs/WORKFLOW.md 2>/dev/null; then
  rule="$(git -C "$DEST" check-ignore -v docs/WORKFLOW.md 2>/dev/null | cut -d: -f3 | cut -f1)"
  echo "CẢNH BÁO: docs/ bị .gitignore nuốt (rule:$rule)." >&2
  echo "Plan/ADR sẽ chỉ nằm local, không vào git — thêm whitelist vào .gitignore nếu muốn version chúng." >&2
fi

# 4. Skill bundle (opt-in): copy toàn bộ skill trong skills/ vào thư mục skill của user.
# Không có flag và stdin là terminal thì hỏi; chạy nền/non-interactive thì bỏ qua.
if [ -z "$WITH_SKILLS" ]; then
  if [ -t 0 ]; then
    printf 'Cài skill bundle (%s skill) vào %s? [y/N] ' "$SKILL_COUNT" "$SKILLS_DIR"
    read -r ans
    case "$ans" in [yY]*) WITH_SKILLS="yes" ;; *) WITH_SKILLS="no" ;; esac
  else
    WITH_SKILLS="no"
  fi
fi

if [ "$WITH_SKILLS" = "yes" ]; then
  mkdir -p "$SKILLS_DIR"
  # Không --delete: skill user tự thêm không bị xóa; bản bundle mới ghi đè bản cũ.
  # README.md/SOURCES.md là metadata của bundle, không phải skill → loại ra.
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude='/README.md' --exclude='/SOURCES.md' \
      "$SRC/skills/" "$SKILLS_DIR/"
  else
    for d in "$SRC/skills/"*/; do cp -rf "$d" "$SKILLS_DIR/"; done
  fi
  echo "đã cài skill bundle vào: $SKILLS_DIR ($(ls "$SKILLS_DIR" | wc -l) mục)"
fi

# 5. Gác cổng pre-commit (githooks): copy script chuẩn + cài vào .git/hooks.
# Idempotent; mặc định warn mode (chỉ log, không chặn commit).
if [ ! -d "$DEST/scripts/githooks" ]; then
  mkdir -p "$DEST/scripts"
  cp -r "$SRC/scripts/githooks" "$DEST/scripts/githooks"
  echo "đã tạo: $DEST/scripts/githooks/"
else
  echo "giữ nguyên (đã có): $DEST/scripts/githooks/"
fi
if [ -d "$DEST/.git" ]; then
  (cd "$DEST" && bash scripts/githooks/install.sh)
else
  echo "bỏ qua cài hook: $DEST chưa phải git repo (chạy scripts/githooks/install.sh sau khi git init)"
fi
