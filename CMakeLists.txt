cmake_minimum_required(VERSION 3.15)
# C нужен только для вендоренной tiny-AES-c (core/src/third_party/tiny_aes).
project(chitubox_utility CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Единая директория для .dll/.so и .exe — удобно для тестов и для
# резолвинга пути к библиотеке из parser_bindings.py при локальном запуске.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

option(SLICER_PARSER_BUILD_TESTS "Собирать юнит-тесты core-библиотеки" ON)

add_subdirectory(core)
