# core-библиотека парсера: DLL под Windows (целевая платформа — MSVC или
# кросс-сборка MinGW-w64 из WSL2, см. README.md), .so — для локальной
# сборки и тестов под Linux.
add_library(slicer_parser SHARED
    src/slicer_parser.cpp
    src/ctb_format.cpp
    src/aes256_cbc.cpp
    src/third_party/tiny_aes/aes.c
)

target_include_directories(slicer_parser
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_definitions(slicer_parser
    PRIVATE
        SLICER_PARSER_EXPORTS
        AES256=1
)

set_target_properties(slicer_parser PROPERTIES
    C_STANDARD 99
    OUTPUT_NAME "slicer_parser"
)

if(MINGW)
    # Самодостаточная .dll без внешних libstdc++-6.dll/libgcc_s_*.dll/
    # libwinpthread-1.dll рядом — совпадает с целью портативной поставки
    # (см. python/packaging/pyinstaller.spec).
    target_link_options(slicer_parser PRIVATE
        -static-libgcc -static-libstdc++ -static
    )
    # По умолчанию CMake под MinGW добавляет "lib" к имени SHARED-таргета
    # (GNU-конвенция), т.е. получилось бы libslicer_parser.dll — а
    # parser_bindings.py/pyinstaller.spec ищут slicer_parser.dll без
    # префикса (как называет DLL сам MSVC). Убираем префикс, чтобы имя
    # файла не зависело от того, чем собран Windows-таргет.
    set_target_properties(slicer_parser PROPERTIES PREFIX "")
endif()

if(SLICER_PARSER_BUILD_TESTS)
    add_subdirectory(tests)
endif()
