include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.15.2
)
# Не переопределяем настройки компилятора/линковки MSVC рантайма у самого
# проекта — используем GoogleTest только для тестов. (Под MinGW это
# no-op — переключатель влияет только на выбор /MD или /MT у MSVC.)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(slicer_parser_tests test_parse_file.cpp)
target_link_libraries(slicer_parser_tests PRIVATE slicer_parser gtest_main)

if(MINGW)
    target_link_options(slicer_parser_tests PRIVATE
        -static-libgcc -static-libstdc++ -static
    )
endif()

set(SLICER_PARSER_EXAMPLES_DIR "${CMAKE_SOURCE_DIR}/examples")
if(WIN32 AND CMAKE_HOST_UNIX)
    # Кросс-сборка под Windows с UNIX-хоста, у которого есть wslpath — это
    # WSL. Тестовый .exe запускается как настоящий Windows-процесс (WSL
    # interop), поэтому ему нужен путь, который понимают файловые API
    # Windows, а не POSIX-путь сборочной машины. `-m` сразу даёт прямые
    # слеши — не нужно экранировать `\` при вставке в строковый литерал.
    find_program(WSLPATH_EXECUTABLE wslpath)
    if(WSLPATH_EXECUTABLE)
        execute_process(
            COMMAND "${WSLPATH_EXECUTABLE}" -m "${CMAKE_SOURCE_DIR}/examples"
            OUTPUT_VARIABLE SLICER_PARSER_EXAMPLES_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
    endif()
endif()

target_compile_definitions(slicer_parser_tests PRIVATE
    EXAMPLES_DIR="${SLICER_PARSER_EXAMPLES_DIR}"
)

include(GoogleTest)
gtest_discover_tests(slicer_parser_tests)
