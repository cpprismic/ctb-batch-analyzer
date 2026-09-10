"""Таблица результатов (ttk.Treeview) + строка «Итого» под ней."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
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
    cost_text: str


class ResultsTable(ttk.Frame):
    _COLUMNS = ("index", "file", "status", "time", "volume", "weight", "layers", "cost")
    _HEADINGS = {
        "index": "№",
        "file": "Файл",
        "status": "Статус",
        "time": "Время печати",
        "volume": "Объём, мл",
        "weight": "Масса, г",
        "layers": "Слоёв",
        "cost": "Стоимость",
    }

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self.tree = ttk.Treeview(
            self, columns=self._COLUMNS, show="headings", height=10
        )
        for column in self._COLUMNS:
            self.tree.heading(column, text=self._HEADINGS[column])
            anchor = tk.W if column == "file" else tk.CENTER
            width = 220 if column == "file" else 40 if column == "index" else 110
            self.tree.column(column, anchor=anchor, width=width)
        self.tree.tag_configure("error", foreground="red")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self._totals_var = tk.StringVar(value="Итого: —")
        base_font = tkfont.nametofont("TkDefaultFont")
        totals_font = tkfont.Font(font=base_font)
        totals_font.configure(size=base_font.cget("size") + 3, weight="bold")
        ttk.Label(
            self, textvariable=self._totals_var, anchor=tk.E, font=totals_font
        ).pack(fill=tk.X, pady=(4, 0))

    def set_rows(self, rows: list[ResultRow]) -> None:
        self.tree.delete(*self.tree.get_children())
        for index, row in enumerate(rows, start=1):
            tags = () if row.status == "OK" else ("error",)
            self.tree.insert(
                "",
                tk.END,
                values=(
                    index,
                    row.file_name,
                    row.status,
                    row.print_time_text,
                    row.volume_text,
                    row.weight_text,
                    row.layer_count_text,
                    row.cost_text,
                ),
                tags=tags,
            )

    def set_totals_text(self, text: str) -> None:
        self._totals_var.set(text)
