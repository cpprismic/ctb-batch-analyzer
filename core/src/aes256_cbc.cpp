#include "aes256_cbc.h"

// AES256 должен быть определён одинаково во всех единицах трансляции,
// использующих struct AES_ctx (иначе размер контекста разъедется между
// этим файлом и third_party/tiny_aes/aes.c) — задаётся один раз для всей
// core-библиотеки в core/CMakeLists.txt (target_compile_definitions).
//
// aes.h — чистый C-заголовок без extern "C"-guard, а aes.c собирается C-
// компилятором (без mangling) — оборачиваем include сами, иначе линковка
// не найдёт символы (C++ ищет мангленные имена).
extern "C" {
#include "third_party/tiny_aes/aes.h"
}

namespace slicer_parser {

void Aes256CbcDecryptInPlace(const std::array<uint8_t, 32>& key,
                             const std::array<uint8_t, 16>& iv, uint8_t* data,
                             size_t length) {
  struct AES_ctx ctx;
  AES_init_ctx_iv(&ctx, key.data(), iv.data());
  AES_CBC_decrypt_buffer(&ctx, data, length);
}

}  // namespace slicer_parser
