---
name: preflight-edit
description: "Armor around file edits: validate a whole edit script BEFORE mutating anything (preflight), then apply with snapshot recheck. Port of mitsuhiko/agent-stuff unified-edit.ts core. Use in subagent campaigns: workers submit edit scripts, the coordinator runs preflight-edit check/apply."
---

# Preflight Edit Skill

`bin/preflight-edit` takes **one text payload** — a row edit script or a
Codex/apply_patch-style patch — and applies it to files.  The whole plan is
**validated before any file is touched** (preflight).  This is the "armor
around file-editing operations" ported from `unified-edit.ts` in
mitsuhiko/agent-stuff (fuzzy matcher, preflight checks, snapshot recheck,
CRLF/BOM preservation).

## CLI

```
preflight-edit check [script] [--cwd DIR] [--json]   # dry run, never mutates
preflight-edit apply [script] [--cwd DIR] [--json]    # preflight, then apply
```

- `script`: path to a script file, or `-` / omitted to read stdin.
- `--cwd DIR`: base directory for relative paths (default: current dir).
- `--json`: machine-readable output (`{"ok": true/false, ...}`).
- Exit codes: `0` ok · `1` preflight/apply failure · `2` usage error.

`check` is the preflight gate: exit 0 means the plan *would* apply cleanly.
`apply` runs preflight internally, so a single `apply` is enough — use
`check` when you want validation without mutation (e.g. reviewing a
worker's script before deciding).

Preflight failures (all raised **before** any file is mutated):
- anchor text not found → `Could not find the exact text in <path>...`
- anchor matches several places → `Found N occurrences ... must be unique. Please provide more context...`
- empty old text, no-op edit, overlapping edits → explicit errors
- `@DEL` / `@INS.PRE` out of range → explicit errors
- at apply time: `file changed since preflight` if the file moved under us

Anchor matching is fuzzy (whitespace/case of trailing space, smart
quotes/dashes) but **uniqueness is enforced**: an ambiguous anchor fails
instead of guessing. CRLF line endings, BOM, and missing final newline are
preserved. Binary files (null bytes) and non-UTF-8 files are refused.

## Row script format

```
[relative/path/to/file.kt]
@REPLACE
-    val old = 1
+    val old = 2

[src/other.kt]
@INS.PRE 1
+import foo.Bar
@APPEND
+// trailing note
@DEL 10-12
```

Operations: `@INS.PRE N` · `@INS.POST N` · `@INS.BEFORE` (insert before the
`-` anchor block) · `@INS.AFTER` · `@REPLACE` (`-` then `+`, or `+` then `-`;
space-prefixed context rows allowed, `@@` separates hunks) · `@APPEND` ·
`@DEL N-M` (also `@DEL N`, `@DEL N..M`).  A literal leading `+`/`-`/`@` in
content is escaped by doubling it (`++`, `--`, `+@`).

## Patch format (alternative)

```
*** Begin Patch
*** Update File: path/to/file
@@ optional context line
 context
-old line
+new line
*** Add File: path/to/new
+content
*** Delete File: path/to/gone
*** End Patch
```

**Lesson 2026-10-03 (campaign feature-flag-spoofing):** dòng sau `@@` là
*anchor locator* — `old_lines` (context/`-`) được match từ dòng **SAU**
anchor, nên KHÔNG được lặp lại dòng anchor làm dòng body đầu tiên (lỗi phổ
biến của worker: `@@ <line>` rồi ngay dòng sau là ` <line>` hoặc `-<line>`
giống hệt → preflight "Failed to find expected lines"). Muốn replace chính
dòng anchor thì dời anchor lên dòng trước đó (hoặc để `@@` trống + đủ context
trong body).

**Lesson 2026-10-03 (2 lần trong cùng campaign):** khi thêm `<string>` vào
`values*/strings.xml`, KHÔNG anchor vào `</resources>` rồi insert sau nó —
kết quả là XML invalid ("junk after document element", aapt2 fail). Luôn
anchor vào `<string>` cuối cùng (hoặc block cuối) và insert TRƯỚC
`</resources>`. Coordinator nên chạy `python3 -c "import xml.dom.minidom;
minidom.parse(...)"` sau mỗi batch chạm XML.

## Coordinator contract (mẫu SpoofX)

In a campaign, **workers do not edit files directly**.  The edit armor is
enforced by process:

1. **Worker contract** — the worker's handoff ends with the edit script
   (fenced block or a scratch file under the goal's `hidden_files/`).
   Allowed paths are listed in the worker's contract as usual.
2. **Coordinator preflight** — coordinator saves the script and runs
   `preflight-edit check --cwd <repo>`.  On failure it sends the CLI's
   error message **back to the worker verbatim**; the worker fixes the
   script (usually: anchor not unique → add context lines; anchor not
   found → re-read the file) and resubmits.  This is the "nhắc" loop.
3. **Apply** — `preflight-edit apply --cwd <repo>` (preflight runs again
   inside).  The CLI prints a unified diff per file — that diff is the
   reviewer's input.
4. **Review discipline unchanged** — after every applied batch, a
   *different* fresh-eyes reviewer reviews the diff (existing SpoofX rule);
   commit only on approve.

Single-agent sessions can use the CLI directly too: write the script,
`check`, then `apply`.

## Tests

`tests/test_preflight_edit.py` — 19 tests (stdlib `unittest`, no deps):
happy-path ops, every preflight failure mode asserting **files are
untouched**, CRLF/BOM/final-newline preservation, patch add/update/delete,
snapshot recheck, dry-run, JSON output.  Run with
`python3 tests/test_preflight_edit.py`.  Re-run after any change to `bin/`.
