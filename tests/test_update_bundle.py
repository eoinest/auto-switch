"""Application bundle boundary and privacy tests, independent of device parsing."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_update_bundle", ROOT / "tools/build_update_bundle.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class UpdateBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "firmware"
        for name in builder.ALLOWED_PATHS:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(("fixture: " + name + "\n").encode())

    def parse(self, content):
        stream = io.BytesIO(content)
        self.assertEqual(stream.readline(), b"AUTOSWITCH1\n")
        records = {}
        while True:
            line = stream.readline()
            self.assertTrue(line.endswith(b"\n"))
            self.assertLessEqual(len(line), 256)
            header = json.loads(line)
            if header == {"end": True}:
                break
            self.assertEqual(set(header), {"path", "size", "sha256"})
            self.assertNotIn(header["path"], records)
            data = stream.read(header["size"])
            self.assertEqual(len(data), header["size"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), header["sha256"])
            self.assertEqual(stream.read(1), b"\n")
            records[header["path"]] = data
        self.assertEqual(stream.read(), b"")
        return records

    def test_deterministic_complete_bundle_and_binary_framing(self):
        payload = bytes(range(256)) + b'\n{"end":true}\nAUTOSWITCH1\n'
        (self.root / "www/app.js").write_bytes(payload)
        bundle = builder.bundle_bytes(self.root)
        self.assertEqual(bundle, builder.bundle_bytes(self.root))
        records = self.parse(bundle)
        self.assertEqual(tuple(records), builder.ALLOWED_PATHS)
        self.assertEqual(len(records), 12)
        for name, data in records.items():
            self.assertEqual(data, (self.root / name).read_bytes())

    def test_extra_private_files_never_included(self):
        marker = b"PRIVATE-SENTINEL-DO-NOT-BUNDLE"
        for name in ("config.json", "calibration.json", "webrepl_cfg.py", "secrets.py",
                     ".env", "wireless_updates.py", "www/config.json"):
            (self.root / name).write_bytes(marker)
        bundle = builder.bundle_bytes(self.root)
        self.assertNotIn(marker, bundle)
        self.assertEqual(set(self.parse(bundle)), set(builder.ALLOWED_PATHS))

    def test_allowlisted_file_symlink_rejected(self):
        private = Path(self.temp.name) / "private.txt"
        private.write_text("private sentinel")
        target = self.root / "main.py"
        target.unlink()
        target.symlink_to(private)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            builder.bundle_bytes(self.root)

    def test_parent_directory_symlink_rejected(self):
        original = self.root / "www"
        external = Path(self.temp.name) / "assets"
        original.rename(external)
        original.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            builder.bundle_bytes(self.root)

    def test_missing_required_file_rejected(self):
        (self.root / "maintenance.py").unlink()
        with self.assertRaisesRegex(ValueError, "Missing application file"):
            builder.bundle_bytes(self.root)

    def test_file_limit_inclusive(self):
        target = self.root / "main.py"
        target.write_bytes(b"x" * 65536)
        self.assertEqual(len(self.parse(builder.bundle_bytes(self.root))["main.py"]), 65536)
        target.write_bytes(b"x" * 65537)
        with self.assertRaisesRegex(ValueError, "64 KiB"):
            builder.bundle_bytes(self.root)

    def test_total_bundle_limit(self):
        for name in builder.MODULES:
            (self.root / name).write_bytes(b"x" * 65536)
        with self.assertRaisesRegex(ValueError, "512 KiB"):
            builder.bundle_bytes(self.root)

    def test_record_header_limit(self):
        with patch.object(builder, "MAX_HEADER_BYTES", 20):
            with self.assertRaisesRegex(ValueError, "header exceeds"):
                builder.bundle_bytes(self.root)

    def test_atomic_output_and_preserve_on_invalid_source(self):
        output = Path(self.temp.name) / "output" / "auto-switch.asupdate"
        self.assertEqual(builder.build_bundle(self.root, output), output)
        previous = output.read_bytes()
        self.parse(previous)
        (self.root / "main.py").unlink()
        with self.assertRaises(ValueError):
            builder.build_bundle(self.root, output)
        self.assertEqual(output.read_bytes(), previous)
        self.assertEqual(list(output.parent.iterdir()), [output])

    def test_cannot_overwrite_source(self):
        target = self.root / "main.py"
        before = target.read_bytes()
        with self.assertRaisesRegex(ValueError, "overwrite"):
            builder.build_bundle(self.root, target)
        self.assertEqual(target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
