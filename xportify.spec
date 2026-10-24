# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = []
datas += collect_data_files('yt_dlp')
datas += collect_data_files('ytmusicapi')
datas += [('assets', 'assets')]

hiddenimports = []
hiddenimports += collect_submodules('yt_dlp')
hiddenimports += collect_submodules('ytmusicapi')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('httpx')

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Xportify',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico' if sys.platform == 'win32' else None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Xportify',
)
