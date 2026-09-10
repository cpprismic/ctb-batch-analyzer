"""Точка входа GUI.

`gui/` — не self-contained пакет: main_window.py и model.py импортируют
`parser_bindings` (лежит в `python/`, на уровень выше) как плоский модуль,
а не через относительный импорт — так проще запускать напрямую
(`python gui/app.py`) и одинаково собирать в PyInstaller. Поэтому оба
каталога — и `python/`, и `gui/` — добавляются в sys.path здесь же, до
любых импортов из них.
"""

import sys
from pathlib import Path

_GUI_DIR = Path(__file__).resolve().parent
_PYTHON_DIR = _GUI_DIR.parent
for _dir in (_PYTHON_DIR, _GUI_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

import tkinter as tk  # noqa: E402

from main_window import MainWindow  # noqa: E402


def main() -> None:
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
