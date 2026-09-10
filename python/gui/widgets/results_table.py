"""Таблица результатов (ttk.Treeview) + строка «Итого» под ней."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


@dataclass
class ResultRow:
    file_name: str
    status: str
    print_time_text: str
    volume_text: str
    weight_text: str
    layer_count_text: str


class ResultsTable(ttk.Frame):
    _COLUMNS = ("file", "status", "time", "volume", "weight", "layers")
    _HEADINGS = {
        "file": "Файл",
        "status": "Статус",
        "time": "Время печати",
        "volume": "Объём, мл",
        "weight": "Масса, г",
        "layers": "Слоёв",
    }

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self.tree = ttk.Treeview(
            self, columns=self._COLUMNS, show="headings", height=10
        )
        for column in self._COLUMNS:
            self.tree.heading(column, text=self._HEADINGS[column])
            anchor = tk.W if column == "file" else tk.CENTER
            width = 220 if column == "file" else 110
            self.tree.column(column, anchor=anchor, width=width)
        self.tree.tag_configure("error", foreground="red")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self._totals_var = tk.StringVar(value="Итого: —")
        ttk.Label(self, textvariable=self._totals_var, anchor=tk.E).pack(
            fill=tk.X, pady=(4, 0)
        )

    def set_rows(self, rows: list[ResultRow]) -> None:
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            tags = () if row.status == "OK" else ("error",)
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.file_name,
                    row.status,
                    row.print_time_text,
                    row.volume_text,
                    row.weight_text,
                    row.layer_count_text,
                ),
                tags=tags,
            )

    def set_totals_text(self, text: str) -> None:
        self._totals_var.set(text)
