# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('C:\\Users\\e24fv\\デスクトップ\\PharmaVoice\\recording.py', '.'), ('pages', 'pages'), ('.streamlit', '.streamlit'), ('.venv/Lib/site-packages/extra_streamlit_components', 'extra_streamlit_components')]
binaries = []
hiddenimports = ['func.AmiVoice_recognition', 'func.function.Auth', 'func.function.Functions', 'io', 'logging', 'os', 'pickle', 'streamlit', 'sys', 'time', 'pages.data', 'update_pharmacist', 'extra_streamlit_components', 'langchain']
datas += copy_metadata('streamlit')
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\e24fv\\AppData\\Local\\Temp\\tmpwev7sqzd.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='PharmaVoice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='PharmaVoice',
)
