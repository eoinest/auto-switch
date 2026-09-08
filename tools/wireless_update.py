#!/usr/bin/env python3
"""One-time USB provisioning for BOOT-held browser updates (not a flash erase)."""
import argparse
import os
from pathlib import Path
import secrets
import string
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/s2'


def create_credentials():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    secret_file = PRIVATE / 'update-password.txt'
    if not secret_file.exists():
        value = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
        with os.fdopen(os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as stream:
            stream.write(value + '\n')
    os.chmod(secret_file, 0o600)
    value = secret_file.read_text().strip()
    if not 24 <= len(value) <= 63 or not value.isascii() or not value.isalnum():
        raise ValueError('Invalid private update password; inspect file locally')
    cfg = PRIVATE / 'maintenance_cfg.py'
    with os.fdopen(os.open(cfg, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as stream:
        stream.write('PASSWORD = ' + repr(value) + '\n')
    os.chmod(cfg, 0o600)
    return cfg


def provision(port):
    from build_update_bundle import ALLOWED_PATHS
    cfg = create_credentials()
    executable = ROOT / '.venv/bin/mpremote'
    base = [str(executable) if executable.exists() else 'mpremote', 'connect', port]
    # All companion modules go across together; config/calibration are preserved.
    modules = [str(ROOT / 'firmware' / name) for name in ALLOWED_PATHS if '/' not in name]
    subprocess.run(base + ['fs', 'cp'] + modules + [str(cfg), ':'], check=True)
    # Existing application installation already contains www/.
    assets = [str(ROOT / 'firmware' / name) for name in ALLOWED_PATHS if name.startswith('www/')]
    subprocess.run(base + ['fs', 'cp'] + assets + [':www/'], check=True)
    subprocess.run(base + ['reset'], check=True)
    print('Browser updater installed. Update/AP password is in .local/s2/update-password.txt (not printed).')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    usb = sub.add_parser('provision', help='Disconnect battery/servo harness before USB')
    usb.add_argument('--port', required=True)
    args = parser.parse_args()
    try:
        provision(args.port)
    except (OSError, ValueError, subprocess.CalledProcessError):
        print('Provisioning failed. Check USB connection and local settings; no credentials were logged.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
