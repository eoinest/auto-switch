"""Build the Apple Silicon companion and create a shareable .app ZIP."""
from pathlib import Path
import hashlib
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    if sys.platform != 'darwin' or platform.machine() != 'arm64':
        raise SystemExit('This build targets Apple Silicon Macs; build on macOS arm64.')
    destination = ROOT / 'dist/companion'
    work = ROOT / 'build/companion'
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                    '--distpath', str(destination), '--workpath', str(work),
                    str(ROOT / 'companion/packaging/AutoSwitch.spec')], check=True)
    app = destination / 'Auto Switch Setup.app'
    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
    archive = destination / 'AutoSwitch-Setup-0.1.0-macOS-arm64.zip'
    subprocess.run(['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', str(app), str(archive)], check=True)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS.txt').write_text(checksum + '  ' + archive.name + '\n')
    print('Share: ' + str(archive))


if __name__ == '__main__':
    main()
