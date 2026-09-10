#ifndef SLICER_PARSER_SLICE_STATS_H_
#define SLICER_PARSER_SLICE_STATS_H_

#include <cstdint>

// Коды ошибок parse_file(). Значения стабильны — на них опирается
// Python-обёртка (python/parser_bindings.py), менять их без синхронизации
// с ней нельзя.
enum class ParseError : int32_t {
  kOk = 0,
  kFileNotFound = 1,
  kFileTooSmall = 2,
  kUnsupportedFormat = 3,
  kTruncatedData = 4,
};

// Результат разбора одного файла. POD, побайтовый layout фиксирован через
// pack(1) — структура пересекает границу DLL и зеркалируется в Python как
// ctypes.Structure с _pack_ = 1 (см. python/parser_bindings.py). Любое
// изменение полей/порядка должно быть согласовано на обеих сторонах и
// отражено в static_assert(sizeof(SliceStats) == ...) ниже.
#pragma pack(push, 1)
struct SliceStats {
  uint32_t print_time_s;  // Время печати, секунды.
  float volume_ml;        // Объём смолы, миллилитры.
  float weight_g;         // Масса смолы, граммы.
  float embedded_cost;  // Стоимость, зашитая в файл на момент нарезки
                        // (цена могла быть выставлена в Chitubox давно
                        // и не отражать текущую цену смолы — GUI её не
                        // показывает пользователю, пересчитывает сам
                        // по актуальной цене за кг).
  uint32_t layer_count;  // Количество слоёв.
  uint32_t resolution_x;  // Разрешение экрана принтера по X, пикс.
  uint32_t resolution_y;  // Разрешение экрана принтера по Y, пикс.
  int32_t error_code;  // Значение ParseError; kOk, если остальные
                       // поля валидны.
};
#pragma pack(pop)

static_assert(sizeof(SliceStats) == 32,
              "SliceStats должен побайтово совпадать с ctypes.Structure на "
              "Python-стороне — при изменении полей обнови обе стороны");

#endif  // SLICER_PARSER_SLICE_STATS_H_
