"""Юнит-тесты сериализации проекта (project_io.py) — round-trip на реальных
файлах из examples/, без tkinter."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gui.project_io import (  # noqa: E402
    load_project,
    project_from_dict,
    project_to_dict,
    save_project,
)
from parser_bindings import parse_file  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


def test_dict_round_trip_preserves_fields():
    entries = [
        parse_file(EXAMPLES_DIR / "example_1.ctb"),
        parse_file(EXAMPLES_DIR / "example_2.ctb"),
    ]

    data = project_to_dict(entries, price_per_kg=1234.5)
    restored_entries, restored_price = project_from_dict(data)

    assert restored_price == 1234.5
    assert restored_entries == entries


def test_dict_round_trip_preserves_broken_file_error(tmp_path):
    bogus = tmp_path / "broken.ctb"
    bogus.write_bytes(b"\x00" * 64)
    entries = [parse_file(bogus)]

    data = project_to_dict(entries, price_per_kg=0.0)
    restored_entries, _ = project_from_dict(data)

    assert restored_entries == entries
    assert restored_entries[0].error is not None


def test_save_and_load_project_file(tmp_path):
    entries = [parse_file(EXAMPLES_DIR / "example_3.ctb")]
    project_path = tmp_path / "test.ctbproj"

    save_project(entries, price_per_kg=777.0, path=project_path)
    restored_entries, restored_price = load_project(project_path)

    assert restored_price == 777.0
    assert restored_entries == entries


def test_project_from_dict_rejects_unknown_version():
    with pytest.raises(ValueError):
        project_from_dict({"version": 999, "price_per_kg": 0.0, "entries": []})
