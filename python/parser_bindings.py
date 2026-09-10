"""ctypes-обёртка над slicer_parser (core/) — C++ DLL/so с парсером .ctb.

Публичный API модуля: :func:`parse_file`. Всё остальное — детали
загрузки библиотеки и её C-контракта (см. core/include/slicer_parser/).
"""

from __future__ import annotations

import ctypes
import enum
import sys
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path


class ParseError(enum.IntEnum):
    """Зеркало enum class ParseError из core/include/slicer_parser/slice_stats.h.

    Значения должны совпадать 1-в-1 с C++ стороной — при изменении там
    обязательно обновить и здесь.
    """

    OK = 0
    FILE_NOT_FOUND = 1
    FILE_TOO_SMALL = 2
    UNSUPPORTED_FORMAT = 3
    TRUNCATED_DATA = 4


_ERROR_MESSAGES_RU = {
    ParseError.FILE_NOT_FOUND: "файл не найден или не открывается",
    ParseError.FILE_TOO_SMALL: "файл слишком мал для заголовка формата",
    ParseError.UNSUPPORTED_FORMAT: "неподдерживаемый вариант формата .ctb",
    ParseError.TRUNCATED_DATA: "файл повреждён или обрезан",
}


class SliceStats(ctypes.Structure):
    """Побайтовое зеркало struct SliceStats (slice_stats.h).

    _pack_ = 1 обязателен — C++-структура собрана с #pragma pack(push, 1),
    без этого layout на Python-стороне разъедется с C++ на padding'ах.
    """

    _pack_ = 1
    _fields_ = [
        ("print_time_s", ctypes.c_uint32),
        ("volume_ml", ctypes.c_float),
        ("weight_g", ctypes.c_float),
        ("embedded_cost", ctypes.c_float),
        ("layer_count", ctypes.c_uint32),
        ("resolution_x", ctypes.c_uint32),
        ("resolution_y", ctypes.c_uint32),
        ("error_code", ctypes.c_int32),
    ]


assert ctypes.sizeof(SliceStats) == 32, (
    "SliceStats должен быть 32 байта — как и одноимённая структура в C++ "
    "(core/include/slicer_parser/slice_stats.h); если поменялась одна "
    "сторона без другой, здесь сразу упадёт assert, а не молча съедутся "
    "поля"
)


@dataclass
class SliceResult:
    """Результат разбора файла — то, чем пользуется GUI.

    embedded_cost из файла намеренно не выставляется отдельным полем "на
    показ": это цена, зафиксированная в Chitubox на момент нарезки, а не
    текущая цена смолы (см. README.md/docs/format_notes.md) — GUI считает
    актуальную стоимость сам, по весу и текущей цене за кг.
    """

    file_path: Path
    print_time: timedelta
    volume_ml: float
    weight_g: float
    layer_count: int
    error: ParseError | None  # None, если разбор успешен


def _candidate_library_dirs() -> list[Path]:
    """Где искать slicer_parser.dll/.so — и из исходников, и из PyInstaller."""
    dirs = []
    if hasattr(sys, "_MEIPASS"):
        # Собранный PyInstaller .exe — библиотека упакована рядом с ним.
        dirs.append(Path(sys._MEIPASS))
    this_dir = Path(__file__).resolve().parent
    dirs.append(this_dir)
    # Запуск из исходников: библиотека собрана CMake-ом в <repo>/build/bin.
    repo_root = this_dir.parent
    dirs.append(repo_root / "build" / "bin")
    dirs.append(repo_root / "build" / "bin" / "Release")
    dirs.append(repo_root / "build" / "bin" / "Debug")
    return dirs


def _library_filename() -> str:
    if sys.platform == "win32":
        return "slicer_parser.dll"
    if sys.platform == "darwin":
        return "libslicer_parser.dylib"
    return "libslicer_parser.so"


def _load_library() -> ctypes.CDLL:
    filename = _library_filename()
    for directory in _candidate_library_dirs():
        candidate = directory / filename
        if candidate.is_file():
            return ctypes.CDLL(str(candidate))
    searched = ", ".join(str(d / filename) for d in _candidate_library_dirs())
    raise FileNotFoundError(
        f"Не найдена библиотека парсера {filename}. Проверено: {searched}. "
        "Убедитесь, что core-библиотека собрана (cmake --build build)."
    )


_lib = _load_library()
_lib.slicer_parse_file.argtypes = [ctypes.c_char_p, ctypes.POINTER(SliceStats)]
_lib.slicer_parse_file.restype = ctypes.c_int32


def parse_file(path: str | Path) -> SliceResult:
    """Разбирает один файл .ctb. Ошибки парсинга не бросаются исключением —
    они возвращаются в SliceResult.error, чтобы GUI мог показать статус
    «ошибка» по конкретному файлу, не прерывая обработку остальных.
    """
    file_path = Path(path)
    stats = SliceStats()
    rc = _lib.slicer_parse_file(str(file_path).encode("utf-8"), ctypes.byref(stats))

    error = None if rc == ParseError.OK else ParseError(rc)
    if error is not None:
        return SliceResult(
            file_path=file_path,
            print_time=timedelta(0),
            volume_ml=0.0,
            weight_g=0.0,
            layer_count=0,
            error=error,
        )

    return SliceResult(
        file_path=file_path,
        print_time=timedelta(seconds=stats.print_time_s),
        volume_ml=stats.volume_ml,
        weight_g=stats.weight_g,
        layer_count=stats.layer_count,
        error=None,
    )


def error_message_ru(error: ParseError) -> str:
    """Человекочитаемое (по-русски) описание кода ошибки — для GUI."""
    return _ERROR_MESSAGES_RU.get(error, "неизвестная ошибка")
