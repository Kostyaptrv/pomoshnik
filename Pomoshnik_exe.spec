# -*- mode: python ; coding: utf-8 -*-

blocks_to_exclude = [
    'PyQt5',
    'PySide2',
    'wx',
    'IPython',
    'jupyter',
]

a = Analysis(
    ['main_pyqt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/rhymes_dict.json', 'data'),
        ('data/templates.json', 'data'),
        ('assets/qss/dark_theme.qss', 'assets/qss'),
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'engine',
        'engine.rhymes',
        'engine.structure',
        'engine.editor',
        'engine.history',
        'engine.phrases',
        'engine.syllable_counter',
        'engine.rhyme_analyzer',
        'utils',
        'utils.export',
        'ui',
        'ui.pages',
        'ui.pages.home_page',
        'ui.pages.rhymes_page',
        'ui.pages.templates_page',
        'ui.pages.editor_page',
        'ui.pages.songs_page',
        'ui.pages.phrases_page',
        'ui.pages.preview_dialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=blocks_to_exclude,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Помощник',
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
    icon=None,  # Можно добавить: icon='assets/icon.ico'
)
