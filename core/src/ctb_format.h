#ifndef SLICER_PARSER_CTB_FORMAT_H_
#define SLICER_PARSER_CTB_FORMAT_H_

#include <array>
#include <cstddef>
#include <cstdint>

#include "slicer_parser/slice_stats.h"

// Разбор формата "CTB v4 encrypted" (magic 0x12FD0107) — единственный
// вариант, подтверждённый на реальных файлах (см. docs/format_notes.md).
// Обычные cbddlp/ctb v2/незашифрованный ctb v4 сюда не входят — добавляются
// отдельной веткой, когда появится образец файла для проверки.
namespace slicer_parser {

// Magic-число во внешнем (незашифрованном) заголовке.
inline constexpr uint32_t kCtbV4EncryptedMagic = 0x12FD0107;

// Ключ и IV для AES-256-CBC расшифровки служебного заголовка. Это не
// секрет конкретного файла, а константы самого формата — они одинаковы
// для всех файлов CTBv4 encrypted (реверс-инжиниринг: см.
// docs/format_notes.md, источник — открытый код проекта UVtools, MIT).
inline constexpr std::array<uint8_t, 32> kHeaderKey = {
    0xd0, 0x5b, 0x8e, 0x33, 0x71, 0xde, 0x3d, 0x1a, 0xe5, 0x4f, 0x22,
    0xdd, 0xdf, 0x5b, 0xfd, 0x94, 0xab, 0x5d, 0x64, 0x3a, 0x9d, 0x7e,
    0xbf, 0xaf, 0x42, 0x03, 0xf3, 0x10, 0xd8, 0x52, 0x2a, 0xea};
inline constexpr std::array<uint8_t, 16> kHeaderIv = {
    0x0f, 0x01, 0x0a, 0x05, 0x05, 0x0b, 0x06, 0x07,
    0x08, 0x06, 0x0a, 0x0c, 0x0c, 0x0d, 0x09, 0x0f};

// Сколько байт зашифрованного блока реально нужно расшифровать, чтобы
// получить все интересующие нас поля (до material_cost включительно).
// Кратно размеру блока AES (16). Полный блок в файле — 288 байт, но
// остальное (цвет/имя смолы и т.п.) нам не нужно.
inline constexpr size_t kPrintParamsDecryptLen = 128;

// Внешний заголовок файла, 48 байт, plaintext, offset 0.
#pragma pack(push, 1)
struct CtbMainHeader {
  uint32_t magic;
  uint32_t encrypted_header_size;
  uint32_t encrypted_header_offset;
  uint32_t unknown1;
  uint32_t version;
  uint32_t signature_size;
  uint32_t signature_offset;
  uint32_t unknown3;
  uint16_t unknown4;
  uint16_t unknown5;
  uint32_t unknown6;
  uint32_t unknown7;
  uint32_t unknown9;
};
#pragma pack(pop)
static_assert(sizeof(CtbMainHeader) == 48,
              "CtbMainHeader должен быть ровно 48 байт (см. "
              "docs/format_notes.md) — иначе офсеты не совпадут с реальным "
              "файлом");

// Поля расшифрованного служебного заголовка, нужные для сводки (первые
// 116 байт из kPrintParamsDecryptLen = 128 расшифрованных байт; остаток —
// переменная часть с именем машины/смолы, не парсится).
#pragma pack(push, 1)
struct CtbPrintParameters {
  uint64_t checksum;
  uint32_t layer_pointers_offset;
  float display_width_mm;
  float display_height_mm;
  float machine_z_mm;
  uint32_t unknown1;
  uint32_t unknown2;
  float total_height_mm;
  float layer_height_mm;
  float exposure_s;
  float bottom_exposure_s;
  float light_off_delay_s;
  uint32_t bottom_layer_count;
  uint32_t resolution_x;
  uint32_t resolution_y;
  uint32_t layer_count;
  uint32_t large_preview_offset;
  uint32_t small_preview_offset;
  uint32_t print_time_s;
  uint32_t projector_type;
  float bottom_lift_height_mm;
  float bottom_lift_speed;
  float lift_height_mm;
  float lift_speed;
  float retract_speed;
  float material_ml;
  float material_g;
  float material_cost;
};
#pragma pack(pop)
static_assert(sizeof(CtbPrintParameters) == 116,
              "CtbPrintParameters должен быть ровно 116 байт (см. "
              "docs/format_notes.md)");
static_assert(sizeof(CtbPrintParameters) <= kPrintParamsDecryptLen,
              "структура не должна выходить за пределы расшифрованного "
              "буфера");

// Пытается разобрать файл `path` как CTBv4 encrypted. Возвращает
// ParseError::kOk и заполняет `out`, либо возвращает код ошибки (`out` в
// этом случае не трогается, кроме error_code). Не бросает исключений —
// все ошибки ввода-вывода превращаются в код возврата.
ParseError ParseCtbV4Encrypted(const char* utf8_path, SliceStats* out);

}  // namespace slicer_parser

#endif  // SLICER_PARSER_CTB_FORMAT_H_
