#ifndef SLICER_PARSER_AES256_CBC_H_
#define SLICER_PARSER_AES256_CBC_H_

#include <array>
#include <cstddef>
#include <cstdint>

namespace slicer_parser {

// Расшифровка AES-256 в режиме CBC без padding, поверх вендоренной
// реализации tiny-AES-c (core/src/third_party/tiny_aes, Unlicense) —
// собственный AES не пишем, используем проверенную стороннюю реализацию.
//
// `data` расшифровывается на месте (in-place), длина должна быть кратна
// 16 байтам (размер блока AES) — это гарантировано форматом CTBv4 encrypted
// (см. docs/format_notes.md).
void Aes256CbcDecryptInPlace(const std::array<uint8_t, 32>& key,
                             const std::array<uint8_t, 16>& iv, uint8_t* data,
                             size_t length);

}  // namespace slicer_parser

#endif  // SLICER_PARSER_AES256_CBC_H_
