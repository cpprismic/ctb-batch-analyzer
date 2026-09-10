"""Юнит-тесты AppModel: пересчёт итогов и стоимости — без tkinter, на
реальных файлах из examples/ (парсер уже проверен отдельно в
test_parser_bindings.py, здесь фокус на логике суммирования)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gui.model import AppModel  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


def test_totals_sum_across_files():
    model = AppModel()
    model.add_files(
        [EXAMPLES_DIR / "example_1.ctb", EXAMPLES_DIR / "example_2.ctb"]
    )

    totals = model.totals()

    assert totals.total_time.total_seconds() == 16085 + 5250
    assert totals.total_volume_ml == pytest.approx(93.90032958984375 + 66.07450103759766)
    assert totals.total_weight_g == pytest.approx(103.29035949707031 + 72.68195343017578)


def test_cost_uses_current_price_not_embedded_cost():
    model = AppModel()
    model.add_files([EXAMPLES_DIR / "example_1.ctb"])  # weight_g ≈ 103.29

    model.set_price_per_kg(1000.0)  # 1000 за кг → удобно проверять на глаз
    totals = model.totals()

    # cost = weight_g / 1000 * price_per_kg = 0.10329... * 1000 ≈ 103.29
    assert totals.total_cost == pytest.approx(103.29035949707031)


def test_broken_file_excluded_from_totals_but_kept_in_list(tmp_path):
    bogus = tmp_path / "broken.ctb"
    bogus.write_bytes(b"\x00" * 64)

    model = AppModel()
    model.add_files([EXAMPLES_DIR / "example_2.ctb", bogus])

    assert len(model.entries()) == 2
    totals = model.totals()
    # Итог должен учитывать только example_2.ctb, а не считать битый файл
    # нулями/ошибкой в сумме.
    assert totals.total_time.total_seconds() == 5250


def test_remove_file():
    model = AppModel()
    path = EXAMPLES_DIR / "example_3.ctb"
    model.add_files([path])
    assert len(model.entries()) == 1

    model.remove_file(path)
    assert model.entries() == []


def test_add_same_file_twice_is_not_duplicated():
    model = AppModel()
    path = EXAMPLES_DIR / "example_1.ctb"
    model.add_files([path, path])
    assert len(model.entries()) == 1
