# Toolchain-файл для кросс-компиляции slicer_parser.dll/.exe под Windows
# (x86_64) из WSL2/Linux с MinGW-w64. Подключается флагом
# -DCMAKE_TOOLCHAIN_FILE=cmake/mingw-w64-x86_64.toolchain.cmake — см.
# README.md, раздел «Сборка под Windows».
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

# Именно -posix-вариант, а не голые имена (которые через update-alternatives
# могут резолвиться в -win32): сама библиотека/тесты std::thread/std::mutex
# не используют, но GoogleTest (gtest-port.h, GTEST_IS_THREADSAFE) — да, а
# под win32-threading-моделью MinGW <mutex>/<condition_variable> в libstdc++
# не собраны (нет backend'а gthreads) — проверено эмпирически: сборка с
# голым x86_64-w64-mingw32-g++ (там по умолчанию win32-вариант) падает на
# gtest-all.cc с "'mutex' in namespace 'std' does not name a type".
set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc-posix)
set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++-posix)
set(CMAKE_RC_COMPILER x86_64-w64-mingw32-windres)

set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
