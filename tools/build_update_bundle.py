#!/usr/bin/env python3
"""Build a deterministic, application-only .asupdate bundle; never include device settings."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAGIC = b"AUTOSWITCH1\n"
MAX_FILE_BYTES = 64 * 1024
MAX_BUNDLE_BYTES = 512 * 1024
MAX_HEADER_BYTES = 256
# Keep this explicit and synchronized with firmware/maintenance.py. Never glob.
MODULES = (
    "control.py", "calibration.py", "hardware.py", "http_api.py",
    "gateway_client.py", "bench.py", "main.py", "maintenance.py",
)
ASSETS = ("www/index.html", "www/app.js", "www/style.css", "www/update.html")
ALLOWED_PATHS = MODULES + ASSETS


def _source_bytes(root, name):
    source = root / name
    # Refuse aliases even when the target happens to remain inside firmware/.
    # An allowlisted path must never redirect to config or credential files.
    current = root
    for component in Path(name).parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("Symlink not allowed for application file: " + name)
    if not source.is_file():
        raise ValueError("Missing application file: " + name)
    with source.open("rb") as stream:
        content = stream.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Application file exceeds 64 KiB: " + name)
    return content


def bundle_bytes(firmware_dir=None):
    """Snapshot exactly the required files, validating all bounds before writing."""
    root = Path(firmware_dir or ROOT / "firmware").resolve()
    records = [MAGIC]
    total = len(MAGIC)
    for name in ALLOWED_PATHS:
        content = _source_bytes(root, name)
        header = json.dumps({
            "path": name, "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
        if len(header) > MAX_HEADER_BYTES:
            raise ValueError("Record header exceeds 256 bytes: " + name)
        total += len(header) + len(content) + 1
        if total + len(b'{"end":true}\n') > MAX_BUNDLE_BYTES:
            raise ValueError("Application bundle exceeds 512 KiB")
        records.extend((header, content, b"\n"))
    records.append(b'{"end":true}\n')
    return b"".join(records)


def build_bundle(firmware_dir=None, output=None):
    root = Path(firmware_dir or ROOT / "firmware").resolve()
    destination = Path(output or ROOT / "output" / "auto-switch.asupdate")
    if destination.resolve() in {(root / name).resolve() for name in ALLOWED_PATHS}:
        raise ValueError("Bundle destination cannot overwrite an application file")
    content = bundle_bytes(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Validation failure leaves any earlier good artifact unchanged; replacement
    # is atomic within the destination filesystem.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix=".asupdate-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware-dir", type=Path, default=ROOT / "firmware")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "auto-switch.asupdate")
    args = parser.parse_args(argv)
    try:
        result = build_bundle(args.firmware_dir, args.output)
    except (OSError, ValueError) as error:
        # File names and bound failures only; no source bytes or settings values.
        parser.exit(1, "Bundle build failed: " + str(error) + "\n")
    print("Built " + str(result) + " (" + str(result.stat().st_size) + " bytes, "
          + str(len(ALLOWED_PATHS)) + " application files; no device settings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
