"""Exercise the staged-file guard with synthetic secrets in disposable repositories."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SecretGuardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init", "-q")
        shutil.copy(ROOT / ".gitignore", self.root / ".gitignore")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def check(self):
        return subprocess.run([sys.executable, str(ROOT / "tools/check_staged_secrets.py")],
                              cwd=self.root, capture_output=True, text=True)

    def test_forced_add_of_private_file_is_blocked(self):
        self.write(".local/example.txt", "private placeholder")
        self.git("add", "-f", ".local/example.txt")
        self.assertEqual(self.check().returncode, 1)

    def test_reads_staged_secret_even_if_working_copy_was_cleaned(self):
        secret = "synthetic-test-credential-39473"
        self.write(".local/s2/wifi-password.txt", secret + "\n")
        self.write("notes.txt", "value=" + secret)
        self.git("add", "notes.txt")
        self.write("notes.txt", "clean working copy")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(secret, result.stdout + result.stderr)

    def test_private_names_ignored_and_examples_still_trackable(self):
        private = ["firmware/config.json", "firmware/config.office.json",
                   "gateway/launchd.plist", ".env.production", "credentials.json",
                   "wifi-password.txt", "device.key", "original-flash.bin"]
        for name in private:
            self.assertEqual(subprocess.run(["git", "check-ignore", "-q", name],
                                            cwd=self.root).returncode, 0, name)
        for name in ["firmware/config.example.json", "firmware/config.s2-demo.example.json",
                     "gateway/launchd.example.plist", "hardware/cad/config.json"]:
            self.write(name, json.dumps({"password": ""}))
            self.git("add", name)
        self.assertEqual(self.check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
