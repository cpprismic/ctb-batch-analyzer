"""Главное окно: связывает AppModel и виджеты (widgets/)."""

from __future__ import annotations

import csv
import tkinter as tk
from datetime import timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from model import AppModel
from parser_bindings import SliceResult, error_message_ru
from project_io import load_project, save_project
from widgets.file_list import FileListPanel
from widgets.results_table import ResultRow, ResultsTable

_CSV_HEADER = [
    "Файл",
    "Статус",
    "Время печати",
    "Объём, мл",
    "Масса, г",
    "Слоёв",
    "Стоимость",
]


def format_timedelta(value: timedelta) -> str:
    total_seconds = int(value.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours} ч {minutes:02d} мин"


def _row_values(
    entry: SliceResult, model: AppModel
) -> tuple[str, str, str, str, str, str, str]:
    if entry.error is not None:
        return (
            entry.file_path.name,
            f"Ошибка: {error_message_ru(entry.error)}",
            "—",
            "—",
            "—",
            "—",
            "—",
        )
    return (
        entry.file_path.name,
        "OK",
        format_timedelta(entry.print_time),
        f"{entry.volume_ml:.2f}",
        f"{entry.weight_g:.2f}",
        str(entry.layer_count),
        f"{model.cost_for(entry):.2f}",
    )


class MainWindow(ttk.Frame):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.model = AppModel()

        root.title("Батч-анализ файлов нарезки (.ctb)")
        self._build_menu(root)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.file_list = FileListPanel(
            self, on_add=self._on_add_files, on_remove=self._on_remove_files
        )
        self.file_list.pack(fill=tk.X, pady=(0, 8))

        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(controls, text="Цена смолы, за кг:").pack(side=tk.LEFT)
        self.price_var = tk.StringVar(value="0")
        price_entry = ttk.Entry(controls, textvariable=self.price_var, width=10)
        price_entry.pack(side=tk.LEFT, padx=(4, 8))
        price_entry.bind("<KeyRelease>", lambda _event: self._on_price_changed())

        ttk.Button(controls, text="Обновить", command=self._on_refresh).pack(
            side=tk.LEFT
        )

        self.results_table = ResultsTable(self)
        self.results_table.pack(fill=tk.BOTH, expand=True)

    def _build_menu(self, root: tk.Tk) -> None:
        # "Экспорт в CSV…" раньше был отдельной кнопкой в панели controls —
        # перенесён сюда, в меню «Файл», вместе с открытием/сохранением
        # проекта (пункт 1 todo.md).
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Открыть проект…", command=self._on_open_project)
        file_menu.add_command(
            label="Сохранить проект…", command=self._on_save_project
        )
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в CSV…", command=self._on_export_csv)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menu_bar)

    def _on_add_files(self, paths: list[str]) -> None:
        self.model.add_files(paths)
        self._refresh_view()

    def _on_remove_files(self, selected_indices: list[int]) -> None:
        entries = self.model.entries()
        to_remove = [
            entries[i].file_path for i in selected_indices if i < len(entries)
        ]
        for path in to_remove:
            self.model.remove_file(path)
        self._refresh_view()

    def _on_refresh(self) -> None:
        self.model.refresh()
        self._refresh_view()

    def _on_price_changed(self) -> None:
        try:
            price = float(self.price_var.get().replace(",", "."))
        except ValueError:
            price = 0.0
        self.model.set_price_per_kg(price)
        self._refresh_view()

    def _on_export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        # utf-8-sig — чтобы Excel на Windows корректно показал кириллицу.
        with open(path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(_CSV_HEADER)
            for entry in self.model.entries():
                writer.writerow(_row_values(entry, self.model))
        messagebox.showinfo("Экспорт", f"Сохранено: {path}")

    def _on_save_project(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".ctbproj",
            filetypes=[("Проект анализа", "*.ctbproj")],
        )
        if not path:
            return
        save_project(self.model.entries(), self.model.price_per_kg, Path(path))
        messagebox.showinfo("Проект", f"Сохранено: {path}")

    def _on_open_project(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Проект анализа", "*.ctbproj"), ("Все файлы", "*.*")]
        )
        if not path:
            return
        try:
            entries, price = load_project(Path(path))
        except (OSError, ValueError) as exc:
            messagebox.showerror("Проект", f"Не удалось открыть проект: {exc}")
            return
        self.model.load_snapshot(entries, price)
        self.price_var.set(str(price))
        self._refresh_view()

    def _refresh_view(self) -> None:
        entries = self.model.entries()
        self.file_list.set_files([entry.file_path.name for entry in entries])
        self.results_table.set_rows(
            [ResultRow(*_row_values(e, self.model)) for e in entries]
        )

        totals = self.model.totals()
        totals_text = (
            f"Итого: {format_timedelta(totals.total_time)} · "
            f"{totals.total_volume_ml:.2f} мл · "
            f"{totals.total_weight_g:.2f} г · "
            f"стоимость: {totals.total_cost:.2f}"
        )
        self.results_table.set_totals_text(totals_text)
