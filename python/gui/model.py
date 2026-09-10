"""Модель приложения — список файлов и пересчёт итогов.

Никакого tkinter здесь нет специально: это позволяет протестировать логику
пересчёта суммарного времени/объёма/массы и стоимости
(tests/test_model.py) без поднятия окна.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Iterable

# python/ должен быть на sys.path — этим занимается точка входа (app.py) и
# тесты (tests/test_model.py); см. комментарий там же.
from parser_bindings import SliceResult, parse_file


@dataclass
class Totals:
    """Суммарные показатели по всем успешно разобранным файлам."""

    total_time: timedelta
    total_volume_ml: float
    total_weight_g: float
    total_cost: float


class AppModel:
    """Список добавленных файлов + текущая цена смолы за кг."""

    def __init__(self) -> None:
        self._order: list[Path] = []
        self._results: dict[Path, SliceResult] = {}
        self.price_per_kg: float = 0.0

    def add_files(self, paths: Iterable[str | Path]) -> None:
        """Добавляет файлы и сразу их разбирает. Уже добавленные (по пути)
        пропускаются, а не дублируются."""
        for raw_path in paths:
            path = Path(raw_path)
            if path in self._results:
                continue
            self._results[path] = parse_file(path)
            self._order.append(path)

    def remove_file(self, path: str | Path) -> None:
        path = Path(path)
        self._results.pop(path, None)
        if path in self._order:
            self._order.remove(path)

    def refresh(self) -> None:
        """Повторный разбор уже добавленных файлов (кнопка «Обновить»)."""
        for path in self._order:
            self._results[path] = parse_file(path)

    def entries(self) -> list[SliceResult]:
        """Результаты разбора в порядке добавления файлов."""
        return [self._results[path] for path in self._order]

    def set_price_per_kg(self, price: float) -> None:
        self.price_per_kg = price

    def totals(self) -> Totals:
        ok_entries = [entry for entry in self.entries() if entry.error is None]
        total_time = sum((entry.print_time for entry in ok_entries), timedelta())
        total_volume_ml = sum(entry.volume_ml for entry in ok_entries)
        total_weight_g = sum(entry.weight_g for entry in ok_entries)
        total_cost = total_weight_g / 1000.0 * self.price_per_kg
        return Totals(total_time, total_volume_ml, total_weight_g, total_cost)
