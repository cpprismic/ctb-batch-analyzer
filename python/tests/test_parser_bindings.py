"""Интеграционный тест: parser_bindings.parse_file() на тех же эталонных
файлах из examples/, что и core/tests/test_parse_file.cpp — значения
взяты из docs/format_notes.md (перепроверены там при реверс-инжиниринге
формата).
"""

import sys
from datetime import timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser_bindings import ParseError, parse_file  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


@pytest.mark.parametrize(
    "filename,print_time_s,volume_ml,weight_g,layer_count",
    [
        ("example_1.ctb", 16085, 93.90032958984375, 103.29035949707031, 1668),
        ("example_2.ctb", 5250, 66.07450103759766, 72.68195343017578, 578),
        ("example_3.ctb", 8971, 43.407066345214844, 47.747772216796875, 923),
    ],
)
def test_parse_example_files(filename, print_time_s, volume_ml, weight_g, layer_count):
    result = parse_file(EXAMPLES_DIR / filename)

    assert result.error is None
    assert result.print_time == timedelta(seconds=print_time_s)
    assert result.volume_ml == pytest.approx(volume_ml)
    assert result.weight_g == pytest.approx(weight_g)
    assert result.layer_count == layer_count


def test_parse_missing_file_reports_error_without_raising():
    result = parse_file(EXAMPLES_DIR / "does_not_exist.ctb")

    assert result.error is ParseError.FILE_NOT_FOUND


def test_parse_non_ctb_file_reports_unsupported_format(tmp_path):
    bogus = tmp_path / "not_a_slicer_file.ctb"
    bogus.write_bytes(b"\x00" * 64)

    result = parse_file(bogus)

    assert result.error is ParseError.UNSUPPORTED_FORMAT
