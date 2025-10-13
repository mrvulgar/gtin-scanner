# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file для GTIN Scanner Live
Используется для создания исполняемого файла для Windows
"""

import sys
from pathlib import Path

block_cipher = None

# Определяем пути
project_root = Path('.').absolute()

a = Analysis(
    ['gtin_scanner_live.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Добавляем данные Gradio если нужны
    ],
    hiddenimports=[
        'gradio',
        'gradio.blocks',
        'gradio.components',
        'gradio.themes',
        'fastapi',
        'uvicorn',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.loops.auto',
        'PIL._imaging',
        'numpy',
        'fitz',
        'pylibdmtx',
        'pylibdmtx.pylibdmtx',
        'queue',
        'threading',
        'tempfile',
        'csv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
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
    [],
    exclude_binaries=True,
    name='GTIN_Scanner_Live',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Оставляем консоль для логов
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Можно добавить иконку .ico файл
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GTIN_Scanner_Live',
)

