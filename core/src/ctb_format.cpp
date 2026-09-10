#include "ctb_format.h"

#include <array>
#include <cstring>
#include <fstream>
#include <vector>

#include "aes256_cbc.h"

#if defined(_WIN32)
#include <windows.h>
#endif

namespace slicer_parser {
namespace {

#if defined(_WIN32)
// На Windows fstream с std::string-путём в кодировке, отличной от ANSI
// code page, может не открыть файл с не-ASCII символами в пути — поэтому
// путь из UTF-8 конвертируется в wide string и открывается через
// перегрузку ifstream(const wchar_t*) (расширение и у MSVC STL, и у
// libstdc++ MinGW-w64 — но именно перегрузку с "голым" wchar_t*, отсюда
// .c_str() ниже: неявная передача std::wstring резолвится в MSVC через
// шаблонный path-like конструктор, а в libstdc++ MinGW-w64 на нём же
// падает с hard compile error).
std::wstring Utf8ToWide(const char* utf8) {
  int len = MultiByteToWideChar(CP_UTF8, 0, utf8, -1, nullptr, 0);
  if (len <= 0) return std::wstring();
  std::wstring wide(static_cast<size_t>(len) - 1, L'\0');
  MultiByteToWideChar(CP_UTF8, 0, utf8, -1, wide.data(), len);
  return wide;
}

std::ifstream OpenBinary(const char* utf8_path) {
  return std::ifstream(Utf8ToWide(utf8_path).c_str(), std::ios::binary);
}
#else
std::ifstream OpenBinary(const char* utf8_path) {
  return std::ifstream(utf8_path, std::ios::binary);
}
#endif

}  // namespace

ParseError ParseCtbV4Encrypted(const char* utf8_path, SliceStats* out) {
  std::ifstream file = OpenBinary(utf8_path);
  if (!file.is_open()) {
    return ParseError::kFileNotFound;
  }

  file.seekg(0, std::ios::end);
  const std::streamoff file_size = file.tellg();
  file.seekg(0, std::ios::beg);
  if (file_size < static_cast<std::streamoff>(sizeof(CtbMainHeader))) {
    return ParseError::kFileTooSmall;
  }

  CtbMainHeader header{};
  file.read(reinterpret_cast<char*>(&header), sizeof(header));
  if (!file) {
    return ParseError::kFileTooSmall;
  }

  if (header.magic != kCtbV4EncryptedMagic) {
    // Другие варианты формата (cbddlp/ctb v2/незашифрованный ctb v4) пока
    // не поддерживаются — нет проверенного на реальных файлах layout'а
    // (см. docs/format_notes.md, раздел "Не проверено").
    return ParseError::kUnsupportedFormat;
  }

  if (header.encrypted_header_size < kPrintParamsDecryptLen) {
    return ParseError::kTruncatedData;
  }
  const std::streamoff encrypted_end =
      static_cast<std::streamoff>(header.encrypted_header_offset) +
      static_cast<std::streamoff>(header.encrypted_header_size);
  if (encrypted_end > file_size) {
    return ParseError::kTruncatedData;
  }

  file.seekg(static_cast<std::streamoff>(header.encrypted_header_offset),
             std::ios::beg);
  std::vector<uint8_t> buffer(kPrintParamsDecryptLen);
  file.read(reinterpret_cast<char*>(buffer.data()),
            static_cast<std::streamsize>(buffer.size()));
  if (!file) {
    return ParseError::kTruncatedData;
  }

  Aes256CbcDecryptInPlace(kHeaderKey, kHeaderIv, buffer.data(), buffer.size());

  // memcpy вместо reinterpret_cast указателя буфера в CtbPrintParameters*:
  // buffer не гарантированно выровнен под требования структуры, а
  // strict aliasing запрещает читать через несовместимый тип указателя.
  CtbPrintParameters params{};
  std::memcpy(&params, buffer.data(), sizeof(params));

  out->print_time_s = params.print_time_s;
  out->volume_ml = params.material_ml;
  out->weight_g = params.material_g;
  out->embedded_cost = params.material_cost;
  out->layer_count = params.layer_count;
  out->resolution_x = params.resolution_x;
  out->resolution_y = params.resolution_y;
  out->error_code = static_cast<int32_t>(ParseError::kOk);
  return ParseError::kOk;
}

}  // namespace slicer_parser
