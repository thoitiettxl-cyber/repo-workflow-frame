#!/usr/bin/env python3
"""Tests for the preflight-edit CLI.  Run:  python3 tests/test_preflight_edit.py

Covers: happy-path ops, every preflight failure mode (file untouched),
line-ending/BOM preservation, patch format, snapshot recheck, dry-run.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SKILL_DIR, "bin", "preflight-edit")


def load_cli():
    spec = importlib.util.spec_from_loader("preflight_edit", loader=None)
    mod = importlib.util.module_from_spec(spec)
    with open(CLI, "r", encoding="utf-8") as f:
        code = compile(f.read(), CLI, "exec")
    exec(code, mod.__dict__)
    return mod


pe = load_cli()


class CliCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    # -- helpers ---------------------------------------------------------
    def write(self, name, content, binary=False):
        p = os.path.join(self.cwd, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        mode = "wb" if binary else "w"
        kw = {} if binary else {"encoding": "utf-8", "newline": ""}
        with open(p, mode, **kw) as f:
            f.write(content)
        return p

    def read(self, name, binary=False):
        p = os.path.join(self.cwd, name)
        mode = "rb" if binary else "r"
        kw = {} if binary else {"encoding": "utf-8", "newline": ""}
        with open(p, mode, **kw) as f:
            return f.read()

    def cli(self, *argv, script=None):
        return subprocess.run(
            [sys.executable, CLI, "--cwd", self.cwd, *argv],
            input=script, capture_output=True, text=True, timeout=30)

    # -- happy paths ------------------------------------------------------
    def test_replace(self):
        self.write("a.txt", "hello\nworld\n")
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-world\n+WORLD\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt"), "hello\nWORLD\n")

    def test_ins_pre_post_append_del(self):
        self.write("a.txt", "one\ntwo\nthree\n")
        script = ("[a.txt]\n@INS.PRE 1\n+zero\n@INS.POST 2\n+after-two\n"
                  "@APPEND\n+four\n@DEL 4\n")
        r = self.cli("apply", script=script)
        self.assertEqual(r.returncode, 0, r.stderr)
        # one, zero? no: PRE 1 inserts before line 1 -> zero,one,two,three
        # POST 2 inserts after line 2 -> zero,one,after-two,two,three
        # APPEND four -> ...three,four ; DEL 4 deletes line 4 (two)
        self.assertEqual(self.read("a.txt"),
                         "zero\none\nafter-two\nthree\nfour\n")

    def test_ins_before_after_anchor(self):
        self.write("a.txt", "alpha\nbeta\ngamma\n")
        script = "[a.txt]\n@INS.BEFORE\n-beta\n+BEFORE-BETA\n@INS.AFTER\n-gamma\n+AFTER-GAMMA\n"
        r = self.cli("apply", script=script)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt"),
                         "alpha\nBEFORE-BETA\nbeta\ngamma\nAFTER-GAMMA\n")

    def test_replace_with_context_rows(self):
        self.write("a.txt", "def f():\n    x = 1\n    return x\n")
        script = ("[a.txt]\n@REPLACE\n def f():\n-    x = 1\n+    x = 2\n"
                  "     return x\n")
        r = self.cli("apply", script=script)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt"), "def f():\n    x = 2\n    return x\n")

    def test_fuzzy_match_trailing_whitespace(self):
        self.write("a.txt", "key = 1   \n")
        # anchor without trailing spaces still matches (fuzzy), but the
        # untouched part keeps original spacing elsewhere
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-key = 1\n+key = 2\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt"), "key = 2\n")

    def test_patch_update_add_delete(self):
        self.write("old.txt", "a\nb\n")
        patch = ("*** Begin Patch\n"
                 "*** Update File: old.txt\n"
                 "@@\n"
                 " a\n"
                 "-b\n"
                 "+B\n"
                 "*** Add File: new.txt\n"
                 "+hello\n"
                 "*** Delete File: gone.txt\n"
                 "*** End Patch\n")
        self.write("gone.txt", "x\n")
        r = self.cli("apply", script=patch)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("old.txt"), "a\nB\n")
        self.assertEqual(self.read("new.txt"), "hello\n")
        self.assertFalse(os.path.exists(os.path.join(self.cwd, "gone.txt")))

    def test_patch_insert_only_hunk_lands_after_anchor(self):
        # Regression 2026-10-03: a pure-insertion hunk (`@@` anchor + only
        # `+` lines, no context/`-` lines) must insert right after the
        # anchor line, NOT at end of file. The old code appended at EOF,
        # which misplaced 3 insert hunks into ProfileAppsScreen.kt.
        self.write("f.kt", "line1\nline2\nline3\n")
        patch = ("*** Begin Patch\n"
                 "*** Update File: f.kt\n"
                 "@@ line1\n"
                 "+inserted\n"
                 "*** End Patch\n")
        r = self.cli("apply", script=patch)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("f.kt"), "line1\ninserted\nline2\nline3\n")

    # -- preflight failures: nothing may be mutated ------------------------
    def test_not_found_aborts_before_mutation(self):
        self.write("a.txt", "hello\n")
        self.write("b.txt", "keep me\n")
        script = ("[a.txt]\n@REPLACE\n-hello\n+hi\n"
                  "[b.txt]\n@REPLACE\n-missing-anchor\n+xx\n")
        r = self.cli("apply", script=script)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Could not find", r.stderr)
        self.assertEqual(self.read("a.txt"), "hello\n")   # untouched!
        self.assertEqual(self.read("b.txt"), "keep me\n")  # untouched!

    def test_duplicate_anchor_requires_more_context(self):
        self.write("a.txt", "x = 1\nx = 1\n")
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-x = 1\n+x = 2\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("occurrences", r.stderr)
        self.assertIn("must be unique", r.stderr)
        self.assertEqual(self.read("a.txt"), "x = 1\nx = 1\n")

    def test_del_out_of_range(self):
        self.write("a.txt", "one\n")
        r = self.cli("apply", script="[a.txt]\n@DEL 5\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("outside", r.stderr)
        self.assertEqual(self.read("a.txt"), "one\n")

    def test_no_change_rejected(self):
        self.write("a.txt", "same\n")
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-same\n+same\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("No changes", r.stderr)

    def test_parse_error_reports_line(self):
        r = self.cli("apply", script="[a.txt]\n@BOGUS\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown edit operation", r.stderr)

    def test_check_is_dry_run(self):
        self.write("a.txt", "hello\n")
        r = self.cli("check", script="[a.txt]\n@REPLACE\n-hello\n+hi\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dry run", r.stdout)
        self.assertEqual(self.read("a.txt"), "hello\n")  # not mutated

    def test_json_output(self):
        self.write("a.txt", "hello\n")
        r = self.cli("apply", "--json",
                     script="[a.txt]\n@REPLACE\n-hello\n+hi\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["files"][0]["path"], "a.txt")
        self.assertIn("-hello", payload["files"][0]["diff"])

        r = self.cli("apply", "--json",
                     script="[a.txt]\n@REPLACE\n-nope\n+hi\n")
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Could not find", payload["errors"][0]["message"])

    # -- fidelity: line endings, BOM, final newline -------------------------
    def test_crlf_preserved(self):
        self.write("a.txt", "one\r\ntwo\r\n", binary=False)
        # write helper used newline="" so CRLF survives; verify raw bytes
        raw = self.read("a.txt", binary=True)
        self.assertIn(b"\r\n", raw)
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-one\n+ONE\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt", binary=True), b"ONE\r\ntwo\r\n")

    def test_missing_final_newline_preserved(self):
        self.write("a.txt", "one\ntwo")  # no trailing newline
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-one\n+ONE\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.read("a.txt", binary=True), b"ONE\ntwo")

    def test_bom_preserved(self):
        self.write("a.txt", "﻿one\ntwo\n", binary=False)
        r = self.cli("apply", script="[a.txt]\n@REPLACE\n-one\n+ONE\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read("a.txt", binary=True).startswith(b"\xef\xbb\xbf"))

    def test_binary_rejected(self):
        self.write("a.bin", b"\x00\x01\x02", binary=True)
        r = self.cli("apply", script="[a.bin]\n@REPLACE\n-\x00\n+x\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("null bytes", r.stderr)

    # -- snapshot recheck ----------------------------------------------------
    def test_changed_since_preflight(self):
        # "changed since preflight" fires on the snapshot-compare path
        # (kind "write": file was empty at plan time).  Simulate a race:
        # build the plan, mutate the file, then apply -> must refuse.
        self.write("a.txt", "")
        plan = pe.build_plan("[a.txt]\n@APPEND\n+hello\n", self.cwd)
        self.assertEqual(plan["changes"][0]["kind"], "write")
        pe.preflight_plan(plan)
        self.write("a.txt", "someone else\n")
        with self.assertRaises(pe.EditError) as ctx:
            pe.apply_plan(plan)
        self.assertIn("changed since preflight", str(ctx.exception))
        self.assertEqual(self.read("a.txt"), "someone else\n")

    def test_changed_file_fails_loudly_on_update_path(self):
        # Non-empty files go through the whole-content re-derivation path:
        # a mid-race change surfaces as a not-found error, also pre-write.
        self.write("a.txt", "v1\n")
        plan = pe.build_plan("[a.txt]\n@REPLACE\n-v1\n+v2\n", self.cwd)
        pe.preflight_plan(plan)
        self.write("a.txt", "v1 - someone else\n")
        with self.assertRaises(pe.EditError) as ctx:
            pe.apply_plan(plan)
        self.assertIn("Could not find", str(ctx.exception))
        self.assertEqual(self.read("a.txt"), "v1 - someone else\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
