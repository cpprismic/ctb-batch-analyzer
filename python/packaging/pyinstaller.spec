# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-спека для сборки портативного .exe (см. README.md, раздел
«Сборка под Windows»).

Запускать из каталога python/:
    pyinstaller packaging/pyinstaller.spec

Ожидает, что core-библиотека уже собрана CMake-ом (../build/bin/…) — иначе
парсер внутри .exe будет отсутствовать (parser_bindings.py в этом случае
упадёт с понятной ошибкой при старте, а не молча).
"""

import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent  # .../python (спека лежит в packaging/)
REPO_ROOT = ROOT.parent

_DLL_NAME = "slicer_parser.dll" if sys.platform == "win32" else "libslicer_parser.so"
_dll_path = REPO_ROOT / "build" / "bin" / _DLL_NAME
binaries = [(str(_dll_path), ".")] if _dll_path.is_file() else []
if not binaries:
    print(f"[pyinstaller.spec] ВНИМАНИЕ: {_dll_path} не найден — соберите "
          f"core (cmake --build build) перед упаковкой .exe")

a = Analysis(
    [str(ROOT / "gui" / "app.py")],
    pathex=[str(ROOT), str(ROOT / "gui")],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

# Единый .exe (one-file режим: a.binaries/a.zipfiles/a.datas передаются
# прямо в EXE, без отдельного COLLECT) — раздел 5 task.md требует именно
# портативный однофайловый .exe.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="chitubox_batch_analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    runtime_tmpdir=None,
)
