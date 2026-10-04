#!/usr/bin/env bash
# secret-scan.sh — deterministic heuristic scan for leaked secrets in a diff.
#
# Usage:  git diff --cached | scripts/secret-scan.sh
#         scripts/secret-scan.sh < diff.txt
#
# Scans ADDED lines only. Exit 1 if any pattern hits (triage manually),
# exit 0 if clean. Matched values are masked in output — never paste a
# suspected real secret into chat/logs; refer by pattern type only.
# This is a NET, not a guarantee: a clean result does NOT prove no secrets.
# Pattern idea adapted from alibaba/open-code-review's allowlist
# (deterministic pre-LLM check).
set -uo pipefail

PATTERNS=(
  "AKIA[0-9A-Z]{16}|aws_secret_access_key"
  "ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}|gho_[A-Za-z0-9]{36}|ghu_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|ghr_[A-Za-z0-9]{36}"
  "sk-ant-[A-Za-z0-9_-]{10,}|sk-[A-Za-z0-9]{20,}"
  "xox[baprs]-[A-Za-z0-9-]{10,}"
  "AIza[0-9A-Za-z_-]{35}"
  "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
  "[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd][\"']?[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{8,}"
  "[Ss][Ee][Cc][Rr][Ee][Tt][\"']?[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{8,}"
  "[Aa][Pp][Ii][_-]?[Kk][Ee][Yy][\"']?[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{8,}"
  "[Aa][Uu][Tt][Hh][_-]?[Tt][Oo][Kk][Ee][Nn][\"']?[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{8,}"
)

added="$(grep -E '^\+' | grep -v '^+++')"
[ -z "$added" ] && exit 0

hits=0
while IFS= read -r line; do
  for pat in "${PATTERNS[@]}"; do
    if printf '%s\n' "$line" | grep -Eq -- "$pat"; then
      masked="$(printf '%s\n' "$line" | sed -E "s/$pat/<REDACTED>/g")"
      printf 'HIT: %s\n' "${masked:0:160}"
      hits=$((hits + 1))
      break
    fi
  done
done <<< "$added"

if [ "$hits" -gt 0 ]; then
  echo "secret-scan: $hits hit(s) — triage manually (heuristics, not proof)" >&2
  exit 1
fi
exit 0
