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

splash = Splash(
    'resources\\gui\\icons\\as64plus.png',
    binaries=a.binaries,
    datas=a.datas
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    splash,            
    splash.binaries,
    [],
    exclude_binaries=True,
    name='AutoSplit64plus',
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
    icon=['resources\\gui\\icons\\as64plus.ico'],
    contents_directory='.'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoSplit64plus',
)
