# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['AutoSplit64.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('defaults.ini', '.'),
        ('logic', 'logic'),
        ('resources', 'resources'), 
        ('routes', 'routes'),
        ('templates', 'templates')
    ],
    hiddenimports=[
        'tf_keras',
        'tf_keras.src',
        'tf_keras.models',
        'tf_keras.layers',
        'tf_keras.utils',
        'tf_keras.src.engine',
        'tf_keras.src.engine.base_layer',
        'tf_keras.src.engine.base_layer_v1',
        'tf_keras.src.engine.input_layer',
        'tf_keras.src.engine.training',
        'tf_keras.src.optimizers',
        'tf_keras.src.losses'
    ],
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
    icon=['resources\\gui\\icons\\icon.ico'],
    contents_directory='.'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoSplit64',
)
