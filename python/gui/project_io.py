"""Сериализация проекта (список разобранных файлов + цена) в JSON.

Хранится полный снимок SliceResult, а не только пути к файлам — чтобы
проект можно было открыть, даже если исходные .ctb-файлы недоступны
(перемещены/удалены). За актуальность данных относительно текущего
состояния файла на диске отвечает пользователь: кнопка «Обновить» в GUI
после открытия проекта пересчитает всё заново через parse_file.

Без tkinter специально — как и model.py, чтобы логику можно было
unit-тестировать без поднятия окна (см. tests/test_project_io.py).
"""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from parser_bindings import ParseError, SliceResult

_PROJECT_VERSION = 1


def project_to_dict(entries: list[SliceResult], price_per_kg: float) -> dict:
    return {
        "version": _PROJECT_VERSION,
        "price_per_kg": price_per_kg,
        "entries": [_entry_to_dict(entry) for entry in entries],
    }


def project_from_dict(data: dict) -> tuple[list[SliceResult], float]:
    version = data.get("version")
    if version != _PROJECT_VERSION:
        raise ValueError(f"unsupported project file version: {version!r}")
    price_per_kg = float(data.get("price_per_kg", 0.0))
    entries = [_entry_from_dict(item) for item in data.get("entries", [])]
    return entries, price_per_kg


def save_project(
    entries: list[SliceResult], price_per_kg: float, path: str | Path
) -> None:
    data = project_to_dict(entries, price_per_kg)
    with open(path, "w", encoding="utf-8") as project_file:
        json.dump(data, project_file, ensure_ascii=False, indent=2)


def load_project(path: str | Path) -> tuple[list[SliceResult], float]:
    with open(path, "r", encoding="utf-8") as project_file:
        data = json.load(project_file)
    return project_from_dict(data)


def _entry_to_dict(entry: SliceResult) -> dict[str, Any]:
    return {
        "file_path": str(entry.file_path),
        "print_time_s": entry.print_time.total_seconds(),
        "volume_ml": entry.volume_ml,
        "weight_g": entry.weight_g,
        "layer_count": entry.layer_count,
        "error": entry.error.value if entry.error is not None else None,
    }


def _entry_from_dict(data: dict[str, Any]) -> SliceResult:
    error_value = data.get("error")
    return SliceResult(
        file_path=Path(data["file_path"]),
        print_time=timedelta(seconds=data["print_time_s"]),
        volume_ml=data["volume_ml"],
        weight_g=data["weight_g"],
        layer_count=data["layer_count"],
        error=ParseError(error_value) if error_value is not None else None,
    )
