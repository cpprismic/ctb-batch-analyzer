#include "slicer_parser/slicer_parser.h"

#include "ctb_format.h"

namespace {

// Единственный поддерживаемый на сегодня вариант формата — CTBv4
// encrypted (см. docs/format_notes.md). Когда появится образец файла
// другой версии (обычный cbddlp/ctb v2, незашифрованный ctb v4, .phz),
// сюда добавляется ветка по magic-числу — сам API (slicer_parse_file)
// не меняется.
ParseError Dispatch(const char* utf8_path, SliceStats* out) {
  return slicer_parser::ParseCtbV4Encrypted(utf8_path, out);
}

}  // namespace

extern "C" int32_t slicer_parse_file(const char* utf8_path, SliceStats* out) {
  if (out == nullptr) {
    return static_cast<int32_t>(ParseError::kFileNotFound);
  }
  *out = SliceStats{};

  if (utf8_path == nullptr) {
    out->error_code = static_cast<int32_t>(ParseError::kFileNotFound);
    return out->error_code;
  }

  // Граница extern "C" не должна пропускать исключения C++ наружу —
  // любая непредвиденная ошибка превращается в код возврата.
  try {
    const ParseError result = Dispatch(utf8_path, out);
    out->error_code = static_cast<int32_t>(result);
    return out->error_code;
  } catch (...) {
    out->error_code = static_cast<int32_t>(ParseError::kTruncatedData);
    return out->error_code;
  }
}
