# -*- mode: python ; coding: utf-8 -*-
import os

# Custom application icon in the project root
app_icon = 'app_icon2.ico' if os.path.exists('app_icon2.ico') else 'app_icon.ico'

datas = []
for ico in ['app_icon2.ico', 'app_icon.ico', 'icon.ico']:
    if os.path.exists(ico):
        datas.append((ico, '.'))

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
