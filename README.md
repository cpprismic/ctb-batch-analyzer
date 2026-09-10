# Батч-анализ файлов нарезки (.ctb)

Windows-утилита: принимает список нарезанных файлов (`.ctb`), парсит из
каждого время печати, объём и массу смолы, показывает сводную таблицу и
итоги (в т.ч. стоимость по заданной цене смолы за кг), умеет экспортировать
результат в CSV.

Архитектура: C++ библиотека-парсер (DLL, плоский C API) + Python/tkinter
GUI, вызывающий DLL через `ctypes`.

- Структура директорий, код-стайл, языковые конвенции — [`STYLE.md`](STYLE.md).
- Как устроен сам формат `.ctb` и что про него выяснено —
  [`docs/format_notes.md`](docs/format_notes.md).

Поддерживаемый на сегодня вариант формата — **CTBv4 с зашифрованным
служебным заголовком** (magic `0x12FD0107`; такой создают, например, новые
версии Chitubox и принтеры вроде Elegoo Mars 3).

## Сборка и запуск под Linux (разработка/тесты)

Годится для правки логики парсера и GUI и прогона тестов — не даёт
Windows-`.exe`.

```sh
# C++ core + юнит-тесты (GoogleTest подтягивается через FetchContent)
cmake -S . -B build
cmake --build build -j
./build/bin/slicer_parser_tests

# Python: биндинги + модель + GUI
python3 -m venv .venv && source .venv/bin/activate
pip install -r python/requirements.txt
python3 -m pytest python/tests/
python3 python/gui/app.py
```

## Сборка под Windows (целевая платформа)

### Вариант 1 — кросс-компиляция из WSL2 (рекомендуется)

Не требует переключения в PowerShell/cmd и Visual Studio Build Tools —
достаточно MinGW-w64 (`x86_64-w64-mingw32-gcc`/`g++`), установленного внутри
WSL2. Собранный кросс-компилятором `.exe` можно сразу запускать прямо из
WSL bash — WSL передаёт такой процесс настоящему ядру Windows (interop),
Wine не нужен.

1. **C++ core (DLL + тесты)**:

   ```sh
   cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=cmake/mingw-w64-x86_64.toolchain.cmake
   cmake --build build -j
   ./build/bin/slicer_parser_tests.exe
   ```

   Результат — `build/bin/slicer_parser.dll` и
   `build/bin/slicer_parser_tests.exe`, оба без внешних рантайм-DLL
   (статически слинкованы libgcc/libstdc++/libwinpthread). Тесты гоняются
   на файлах из `examples/` через настоящий Windows-процесс — если
   что-то не так с окружением, это будет видно сразу (проверено: 8/8
   тестов зелёные).

   Если до этого `build/` уже был сконфигурирован под Linux (`.so`) —
   тулчейн в существующем кэше не подменить, сначала `rm -rf build`.

2. **Python-окружение и упаковка** — те же шаги и команды, что в
   Варианте 2 (пп. 2-3): DLL из этой сборки `parser_bindings.py` и
   `pyinstaller.spec` находят по тому же пути `build/bin/`, без правок.
   Учтите только, что PyInstaller **не кросс-компилирует** — сам
   `pyinstaller` всё равно нужно запускать под настоящим
   Windows-интерпретатором Python (не под Python из WSL), даже если DLL
   внутри собрана в WSL.

### Вариант 2 — нативная сборка на Windows (MSVC)

Если WSL или MinGW недоступны: из PowerShell/cmd с установленными Visual
Studio Build Tools (или полной Visual Studio) с компонентом "Desktop
development with C++".

1. **C++ core (DLL)**:

   ```powershell
   cmake -S . -B build -A x64
   cmake --build build --config Release
   ```

   Результат — `build\bin\Release\slicer_parser.dll` и
   `build\bin\Release\slicer_parser_tests.exe`. Прогоните тесты
   (`.\build\bin\Release\slicer_parser_tests.exe`) — все они гоняются на
   файлах из `examples/`, если что-то не так с окружением, это будет видно
   сразу.

2. **Python-окружение**:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r python\requirements.txt
   python -m pytest python\tests\
   python python\gui\app.py   # ручная проверка GUI
   ```

3. **Упаковка в портативный `.exe`** (PyInstaller подхватит DLL из
   `build\bin\Release\` или `build\bin\` — см. `python/packaging/pyinstaller.spec`):

   ```powershell
   cd python
   pyinstaller packaging\pyinstaller.spec
   ```

   Готовый файл — `python\dist\chitubox_batch_analyzer.exe`.
