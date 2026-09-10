#ifndef SLICER_PARSER_SLICER_PARSER_H_
#define SLICER_PARSER_SLICER_PARSER_H_

#include "slicer_parser/slice_stats.h"

// Экспорт символов из DLL на Windows; на остальных платформах (сборка .so
// для локальной разработки/тестов под Linux) не нужен.
#if defined(_WIN32)
#if defined(SLICER_PARSER_EXPORTS)
#define SLICER_PARSER_API __declspec(dllexport)
#else
#define SLICER_PARSER_API __declspec(dllimport)
#endif
#else
#define SLICER_PARSER_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Разбирает один файл нарезки (.ctb) и заполняет `out`.
//
// `utf8_path` — путь к файлу в кодировке UTF-8 (на Windows внутри
// декодируется в widechar-путь, чтобы корректно работать с не-ASCII
// именами файлов).
//
// Возвращает значение ParseError (0 = ParseError::kOk). Тот же код
// дублируется в `out->error_code`. Исключения C++ никогда не пересекают
// эту границу — все ошибки внутри перехватываются и превращаются в код
// возврата.
SLICER_PARSER_API int32_t slicer_parse_file(const char* utf8_path,
                                            SliceStats* out);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // SLICER_PARSER_SLICER_PARSER_H_
