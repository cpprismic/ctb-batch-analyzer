// Юнит-тесты slicer_parse_file() на реальных файлах из examples/ (см.
// docs/format_notes.md — эталонные значения получены и перепроверены там
// же при реверс-инжиниринге формата) плюс несколько негативных кейсов.

#include <gtest/gtest.h>

#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

#include "slicer_parser/slicer_parser.h"

namespace {

std::string ExamplePath(const char* filename) {
  return std::string(EXAMPLES_DIR) + "/" + filename;
}

// Пишет `bytes` в новый временный файл и возвращает путь к нему; файл
// удаляется в конце теста (SetUp/TearDown fixture ниже).
class TempFile {
 public:
  explicit TempFile(const std::vector<uint8_t>& bytes) {
    path_ =
        (std::filesystem::temp_directory_path() / "slicer_parser_test_tmp.bin")
            .string();
    std::ofstream out(path_, std::ios::binary);
    out.write(reinterpret_cast<const char*>(bytes.data()),
              static_cast<std::streamsize>(bytes.size()));
  }
  ~TempFile() { std::remove(path_.c_str()); }
  const char* c_str() const { return path_.c_str(); }

 private:
  std::string path_;
};

}  // namespace

TEST(SlicerParser, Example1) {
  SliceStats stats{};
  const int32_t rc =
      slicer_parse_file(ExamplePath("example_1.ctb").c_str(), &stats);
  ASSERT_EQ(rc, static_cast<int32_t>(ParseError::kOk));
  EXPECT_EQ(stats.print_time_s, 16085u);
  EXPECT_EQ(stats.layer_count, 1668u);
  EXPECT_EQ(stats.resolution_x, 11520u);
  EXPECT_EQ(stats.resolution_y, 5120u);
  EXPECT_FLOAT_EQ(stats.volume_ml, 93.90032958984375f);
  EXPECT_FLOAT_EQ(stats.weight_g, 103.29035949707031f);
  EXPECT_FLOAT_EQ(stats.embedded_cost, 206.58071899414062f);
}

TEST(SlicerParser, Example2) {
  SliceStats stats{};
  const int32_t rc =
      slicer_parse_file(ExamplePath("example_2.ctb").c_str(), &stats);
  ASSERT_EQ(rc, static_cast<int32_t>(ParseError::kOk));
  EXPECT_EQ(stats.print_time_s, 5250u);
  EXPECT_EQ(stats.layer_count, 578u);
  EXPECT_FLOAT_EQ(stats.volume_ml, 66.07450103759766f);
  EXPECT_FLOAT_EQ(stats.weight_g, 72.68195343017578f);
  EXPECT_FLOAT_EQ(stats.embedded_cost, 145.36390686035156f);
}

TEST(SlicerParser, Example3) {
  SliceStats stats{};
  const int32_t rc =
      slicer_parse_file(ExamplePath("example_3.ctb").c_str(), &stats);
  ASSERT_EQ(rc, static_cast<int32_t>(ParseError::kOk));
  EXPECT_EQ(stats.print_time_s, 8971u);
  EXPECT_EQ(stats.layer_count, 923u);
  EXPECT_FLOAT_EQ(stats.volume_ml, 43.407066345214844f);
  EXPECT_FLOAT_EQ(stats.weight_g, 47.747772216796875f);
  EXPECT_FLOAT_EQ(stats.embedded_cost, 95.49554443359375f);
}

// Кросс-проверка: cost, зашитый в файл, должен быть согласован с массой
// (см. docs/format_notes.md — во всех образцах cost == 2 * weight_g, это
// не требование формата, а просто ещё одна проверка, что поля не съехали).
TEST(SlicerParser, EmbeddedCostMatchesWeightRatio) {
  for (const char* name : {"example_1.ctb", "example_2.ctb", "example_3.ctb"}) {
    SliceStats stats{};
    ASSERT_EQ(slicer_parse_file(ExamplePath(name).c_str(), &stats),
              static_cast<int32_t>(ParseError::kOk));
    EXPECT_NEAR(stats.embedded_cost, stats.weight_g * 2.0f, 0.01f) << name;
  }
}

TEST(SlicerParser, FileNotFound) {
  SliceStats stats{};
  const int32_t rc = slicer_parse_file("/no/such/file.ctb", &stats);
  EXPECT_EQ(rc, static_cast<int32_t>(ParseError::kFileNotFound));
  EXPECT_EQ(stats.error_code, static_cast<int32_t>(ParseError::kFileNotFound));
}

TEST(SlicerParser, FileTooSmall) {
  TempFile tmp(std::vector<uint8_t>(10, 0));
  SliceStats stats{};
  const int32_t rc = slicer_parse_file(tmp.c_str(), &stats);
  EXPECT_EQ(rc, static_cast<int32_t>(ParseError::kFileTooSmall));
}

TEST(SlicerParser, UnsupportedMagic) {
  // 48 нулевых байт — валидный размер заголовка, но magic не совпадает ни
  // с одним известным вариантом формата.
  TempFile tmp(std::vector<uint8_t>(48, 0));
  SliceStats stats{};
  const int32_t rc = slicer_parse_file(tmp.c_str(), &stats);
  EXPECT_EQ(rc, static_cast<int32_t>(ParseError::kUnsupportedFormat));
}

TEST(SlicerParser, NullOutParam) {
  const int32_t rc = slicer_parse_file("examples/example_1.ctb", nullptr);
  EXPECT_NE(rc, static_cast<int32_t>(ParseError::kOk));
}
