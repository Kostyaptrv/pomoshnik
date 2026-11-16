# -*- mode: python ; coding: utf-8 -*-
"""Spec-файл для сборки приложения Помощник для написания песен."""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Собираем все зависимости
hidden_imports = [
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'fpdf',
    'fpdf2',
    'engine',
    'engine.editor',
    'engine.phrases',
    'engine.rhymes',
    'engine.structure',
    'engine.syllable_counter',
    'engine.history',
    'ui',
    'ui.main_window',
    'ui.pages',
    'ui.pages.home_page',
    'ui.pages.rhymes_page',
    'ui.pages.templates_page',
    'ui.pages.editor_page',
    'ui.pages.songs_page',
    'ui.pages.phrases_page',
    'ui.pages.preview_dialog',
    'ui.components',
    'ui.components.toast',
    'ui.components.loading_overlay',
    'utils',
    'utils.export',
    'utils.logger',
]

a = Analysis(
    ['main_pyqt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/*.json', 'data'),
        ('assets/qss/*.qss', 'assets/qss'),
        ('app_icon.ico', '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'streamlit',
        'textblob',
        'numpy',
        'test_',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Помощник для написания песен',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
    manifest='app.manifest',
)
