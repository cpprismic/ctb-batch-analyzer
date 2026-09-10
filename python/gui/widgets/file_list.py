"""Панель списка добавленных файлов: кнопки + список, без знания о модели —
только колбэки наружу (что и роднит виджет с остальным `gui/`, см. README.md:
логика отделена от виджетов)."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Sequence

FILE_TYPES = [
    ("Файлы нарезки .ctb/.cbddlp", "*.ctb *.cbddlp"),
    ("Все файлы", "*.*"),
]


class FileListPanel(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_add: Callable[[list[str]], None],
        on_remove: Callable[[list[int]], None],
    ) -> None:
        super().__init__(parent)
        self._on_add = on_add
        self._on_remove = on_remove

        self.listbox = tk.Listbox(
            self, selectmode=tk.EXTENDED, height=6, exportselection=False
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        buttons = ttk.Frame(self)
        buttons.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(buttons, text="Добавить файлы…", command=self._handle_add).pack(
            fill=tk.X, pady=(0, 4)
        )
        ttk.Button(
            buttons, text="Удалить выбранное", command=self._handle_remove
        ).pack(fill=tk.X)

    def _handle_add(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Выберите файлы нарезки", filetypes=FILE_TYPES
        )
        if paths:
            self._on_add(list(paths))

    def _handle_remove(self) -> None:
        selected = list(self.listbox.curselection())
        if selected:
            self._on_remove(selected)

    def set_files(self, names: Sequence[str]) -> None:
        self.listbox.delete(0, tk.END)
        for name in names:
            self.listbox.insert(tk.END, name)
