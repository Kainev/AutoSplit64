# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['AutoSplit64.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('routes/README.txt', 'routes'),
        ('defaults.json', '.'),
        ('templates/default*', 'templates'),
        ('.version', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Recursive include of directory, keeping structure, must be done using the Tree class.
a.datas += Tree('resources', prefix='resources')
a.datas += Tree('logic', prefix='logic')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    icon='resources/gui/icons/icon.ico',
    exclude_binaries=True,
    name='AutoSplit64',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoSplit64',
)
