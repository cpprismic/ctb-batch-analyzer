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


def _icon_path() -> Path:
    # Тот же паттерн поиска ресурсов, что и в parser_bindings.py: при сборке
    # PyInstaller файлы из datas распаковываются во временный sys._MEIPASS,
    # при запуске из исходников — берём рядом с gui/.
    base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else _GUI_DIR
    return base / "assets" / "app_icon.png"


def main() -> None:
    root = tk.Tk()
    icon_path = _icon_path()
    if icon_path.is_file():
        try:
            icon_image = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(True, icon_image)
            # Ссылку нужно держать явно — иначе PhotoImage соберёт GC и
            # значок окна слетит после выхода из main().
            root._icon_image_ref = icon_image
        except tk.TclError:
            pass  # отсутствие/повреждение иконки не должно ронять GUI
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
