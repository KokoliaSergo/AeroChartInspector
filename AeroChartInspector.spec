# -*- mode: python ; coding: utf-8 -*-
import os

# Check for custom icon in the project root
icon_candidates = ['app_icon.ico', 'icon.ico', 'assets/icon.ico']
app_icon = next((f for f in icon_candidates if os.path.exists(f)), None)

datas = []
if app_icon:
    datas.append((app_icon, '.'))

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AeroChartInspector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,
)
