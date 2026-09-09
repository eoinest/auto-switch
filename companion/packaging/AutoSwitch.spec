from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

root = Path(SPECPATH).parent.parent
datas = [(str(root / 'companion' / name), '.') for name in ('index.html', 'app.js', 'style.css')]
datas += [(str(root / 'LICENSE'), 'licenses/auto-switch')]
datas += copy_metadata('mpremote') + copy_metadata('pyserial') + copy_metadata('platformdirs') + copy_metadata('pyinstaller')
a = Analysis([str(root / 'companion/desktop.py')], pathex=[str(root / 'companion')],
             binaries=[], datas=datas,
             hiddenimports=collect_submodules('mpremote') + collect_submodules('serial'),
             hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=['tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Auto Switch Setup',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, target_arch='arm64', codesign_identity=None, entitlements_file=None)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='Auto Switch Setup')
app = BUNDLE(coll, name='Auto Switch Setup.app', icon=None,
             bundle_identifier='com.eoinest.autoswitch.setup',
             info_plist={'CFBundleShortVersionString': '0.1.0', 'CFBundleVersion': '1',
                         'LSMinimumSystemVersion': '15.0',
                         'NSHighResolutionCapable': True, 'LSUIElement': True})
