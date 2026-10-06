#!/usr/bin/env python3
"""Self-test for the linkage-checks skill scaffold and template.

stdlib unittest, no deps. Run: python3 tests/test_scaffold.py
"""
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAFFOLD = os.path.join(SKILL_DIR, "bin", "new-linkage-check")
TEMPLATE = os.path.join(SKILL_DIR, "assets", "check-template.sh")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def make_toy_check(repo):
    """Fill the template for a toy pair: DEFINE: <name> lines in defs.txt
    must appear as USE: <name> strings under the use/ tree. Escape hatch:
    a '# NO_USE: <reason>' comment on the line directly above the DEFINE."""
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    tpl = tpl.replace("A_FILE", "DEFS_FILE").replace("B_DIR", "USE_DIR")
    tpl = tpl.replace("export A_FILE B_DIR", "export DEFS_FILE USE_DIR")
    tpl = tpl.replace('a_file = os.environ["A_FILE"]', 'a_file = os.environ["DEFS_FILE"]')
    tpl = tpl.replace('b_dir = os.environ["B_DIR"]', 'b_dir = os.environ["USE_DIR"]')

    parse_a = '''defs = []
lines = src.splitlines()
for i, line in enumerate(lines):
    m = re.match(r"^DEFINE:\\s*([a-z0-9_]+)\\s*$", line)
    if not m:
        continue
    reason = None
    if i > 0:
        hm = re.match(r"^#\\s*NO_USE:\\s*(.+?)\\s*$", lines[i - 1])
        if hm:
            reason = hm.group(1)
    defs.append({"name": m.group(1), "exempt_reason": reason})'''

    scan_b = '''for root, _, files in os.walk(b_dir):
    for fn in files:
        if not fn.endswith(".txt"):
            continue
        text = open(os.path.join(root, fn), encoding="utf-8").read()
        refs.update(re.findall(r"USE:\\s*([a-z0-9_]+)", text))'''

    filled = tpl.replace("# FILL: your regex / parsing here.", parse_a)
    filled = filled.replace(
        "# FILL: walk USE_DIR, collect references with your regex.", scan_b)
    filled = filled.replace('"FILL:things"', '"widgets"')
    filled = filled.replace('"FILL:where"', '"a USE reference"')
    filled = filled.replace('"FILL:MARKER"', '"NO_USE"')
    path = os.path.join(repo, "scripts", "checks", "toy.sh")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(filled)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


def write_fixture(base, defs_text, uses):
    os.makedirs(os.path.join(base, "use"), exist_ok=True)
    with open(os.path.join(base, "defs.txt"), "w", encoding="utf-8") as f:
        f.write(defs_text)
    for i, u in enumerate(uses):
        with open(os.path.join(base, "use", "f%d.txt" % i), "w",
                   encoding="utf-8") as f:
            f.write(u)


class ScaffoldTest(unittest.TestCase):
    def test_scaffold_creates_script_and_fixtures(self):
        repo = tempfile.mkdtemp()
        try:
            r = run([SCAFFOLD, "demo-check", "--repo", repo])
            self.assertEqual(r.returncode, 0, r.stderr)
            script = os.path.join(repo, "scripts", "checks", "demo-check.sh")
            self.assertTrue(os.path.isfile(script))
            self.assertTrue(os.access(script, os.X_OK))
            with open(script, encoding="utf-8") as f:
                body = f.read()
            self.assertIn("FILL:", body)  # still needs filling
            self.assertIn("set -euo pipefail", body)
            for fx in ("pass", "fail", "exempt"):
                d = os.path.join(repo, "scripts", "checks", "tests",
                                 "fixtures", "demo-check", fx)
                self.assertTrue(os.path.isdir(d), d)
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_scaffold_rejects_bad_name(self):
        r = run([SCAFFOLD, "Bad_Name", "--repo", tempfile.mkdtemp()])
        self.assertNotEqual(r.returncode, 0)

    def test_scaffold_refuses_overwrite(self):
        repo = tempfile.mkdtemp()
        try:
            self.assertEqual(run([SCAFFOLD, "x", "--repo", repo]).returncode, 0)
            r = run([SCAFFOLD, "x", "--repo", repo])
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("already exists", r.stderr)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


class TemplateBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.script = make_toy_check(self.repo)
        self.fx = os.path.join(self.repo, "fx")
        os.makedirs(self.fx)

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def run_check(self, name):
        base = os.path.join(self.fx, name)
        env = dict(os.environ, DEFS_FILE=os.path.join(base, "defs.txt"),
                   USE_DIR=os.path.join(base, "use"))
        return run(["bash", self.script], env=env)

    def test_pass(self):
        write_fixture(os.path.join(self.fx, "pass"),
                      "DEFINE: alpha\nDEFINE: beta\n",
                      ["USE: alpha\n", "USE: beta\n"])
        r = self.run_check("pass")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS:", r.stdout)

    def test_fail_names_offender(self):
        write_fixture(os.path.join(self.fx, "fail"),
                      "DEFINE: alpha\nDEFINE: gamma\n",
                      ["USE: alpha\n"])
        r = self.run_check("fail")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL:", r.stdout)
        self.assertIn("gamma", r.stdout)
        self.assertNotIn("alpha", r.stdout.split("FAIL:")[1].split("\n")[0])

    def test_exempt(self):
        write_fixture(os.path.join(self.fx, "exempt"),
                      "DEFINE: alpha\n# NO_USE: internal only\nDEFINE: beta\n",
                      ["USE: alpha\n"])
        r = self.run_check("exempt")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS:", r.stdout)
        self.assertIn("beta", r.stdout)  # listed as exempt

    def test_marker_wrong_scope_does_not_exempt(self):
        # Marker two lines above (not directly attached) must NOT exempt.
        write_fixture(os.path.join(self.fx, "scope"),
                      "DEFINE: alpha\n# NO_USE: internal only\n\nDEFINE: beta\n",
                      ["USE: alpha\n"])
        r = self.run_check("scope")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("beta", r.stdout)

    def test_empty_definitions_is_misconfiguration(self):
        write_fixture(os.path.join(self.fx, "empty"), "nothing here\n", ["x\n"])
        r = self.run_check("empty")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
