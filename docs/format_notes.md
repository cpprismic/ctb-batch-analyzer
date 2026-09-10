# Заметки по формату .ctb

Живой документ: что реально выяснено про формат по мере выполнения раздела 1
`task.md`. В отличие от `task.md` (список задач) здесь фиксируются
конкретные результаты — офсеты, версии, на каких файлах проверено.

## Проверено на файлах

`examples/example_1.ctb`, `examples/example_2.ctb`, `examples/example_3.ctb`
(3 реальных нарезанных файла, предоставлены пользователем).

Все три — **один и тот же вариант формата**: CTBv4 с зашифрованным служебным
заголовком ("CTB encrypted", magic `0x12FD0107`). Это формат, который
используют, в частности, Elegoo Mars 3 (Pro) и близкие принтеры/профили с
новых версий Chitubox. Обычный `cbddlp` (magic `0x12FD0019`), `ctb v2`
(`0x12FD0086`) и незашифрованный `ctb v4` (`0x12FD0106`) в имеющихся образцах
не встречаются — код для них пока не пишем (см. «Не проверено» ниже).

## Magic-значения (для справки, что ещё может встретиться)

| Magic | Формат | В наших файлах? |
|---|---|---|
| `0x12FD0019` | cbddlp (v1–v2) | нет |
| `0x12FD0086` | ctb (v2–v3) | нет |
| `0x12FD0106` | ctb v4 (незашифрованный) | нет |
| `0x12FD0107` | **ctb v4 encrypted** | **да, все 3 файла** |

## Внешний заголовок (48 байт, plaintext, offset 0)

Little-endian, без выравнивания (упаковано по 1 байту):

| Offset | Поле | Тип | Комментарий |
|---|---|---|---|
| 0x00 | `magic` | u32 | `0x12FD0107` |
| 0x04 | `encrypted_header_size` | u32 | 288 у всех 3 файлов |
| 0x08 | `encrypted_header_offset` | u32 | 48 у всех 3 файлов |
| 0x0C | `unknown1` | u32 | 0 |
| 0x10 | `version` | u32 | 4 |
| 0x14 | `signature_size` | u32 | 32 |
| 0x18 | `signature_offset` | u32 | указывает в конец файла (подпись) |
| 0x1C | `unknown3` | u32 | 0 |
| 0x20 | `unknown4` | u16 | 1 |
| 0x22 | `unknown5` | u16 | 1 |
| 0x24 | `unknown6` | u32 | 0 |
| 0x28 | `unknown7` | u32 | разное значение на файл, не используется |
| 0x2C | `unknown9` | u32 | 0 |

## Зашифрованный блок (288 байт по `encrypted_header_offset`)

AES-256-CBC, **без padding** (288 — кратно 16 байтам блока). Ключ и IV — не
индивидуальные для файла, а константы самого формата (расшифровки с ними
работают на всех 3 образцах):

```
key = XOR(base64_decode("hQ36XB6yTk+zO02ysyiowt8yC1buK+nbLWyfY40EXoU="), "UVtools")  # 32 байта
iv  = XOR(base64_decode("Wld+ampndVJecmVjYH5cWQ=="), "UVtools")                      # 16 байт
```

(XOR — побайтово, ключ "UVtools" повторяется циклически.)

Расшифрованные поля, нужные нам (little-endian, offset — внутри
расшифрованного блока; для их извлечения достаточно расшифровать первые 128
байт = 8 AES-блоков, дальше не нужно):

| Offset | Поле | Тип |
|---|---|---|
| 0x00 | `checksum` | u64 |
| 0x08 | `layer_pointers_offset` | u32 |
| 0x0C | `display_width_mm` | f32 |
| 0x10 | `display_height_mm` | f32 |
| 0x14 | `machine_z_mm` | f32 |
| 0x18 | `unknown1` | u32 |
| 0x1C | `unknown2` | u32 |
| 0x20 | `total_height_mm` | f32 |
| 0x24 | `layer_height_mm` | f32 |
| 0x28 | `exposure_s` | f32 |
| 0x2C | `bottom_exposure_s` | f32 |
| 0x30 | `light_off_delay_s` | f32 |
| 0x34 | `bottom_layer_count` | u32 |
| 0x38 | `resolution_x` | u32 |
| 0x3C | `resolution_y` | u32 |
| 0x40 | `layer_count` | u32 |
| 0x44 | `large_preview_offset` | u32 |
| 0x48 | `small_preview_offset` | u32 |
| 0x4C | `print_time_s` | u32 |
| 0x50 | `projector_type` | u32 |
| 0x54 | `bottom_lift_height_mm` | f32 |
| 0x58 | `bottom_lift_speed` | f32 |
| 0x5C | `lift_height_mm` | f32 |
| 0x60 | `lift_speed` | f32 |
| 0x64 | `retract_speed` | f32 |
| 0x68 | `material_ml` | f32 |
| 0x6C | `material_g` | f32 |
| 0x70 | `material_cost` | f32 |

## Кросс-проверка на реальных данных

Расшифровка была проверена локально (Python + pycryptodome) на всех 3
файлах. Два независимых факта подтверждают, что раскладка полей верна:

1. `total_height_mm / layer_height_mm` совпадает с `layer_count` (с точностью
   до округления) на всех 3 файлах.
2. `material_cost` ровно в 2 раза больше `material_g` на всех 3 файлах — то
   есть при нарезке в Chitubox была выставлена одна и та же цена смолы
   (2.0 за грамм в валюте пользователя), что физически осмысленно.

| Файл | Высота/шаг слоя → слоёв | Факт. слоёв | Время | Объём, мл | Масса, г | cost |
|---|---|---|---|---|---|---|
| example_1.ctb | 83.4/0.05≈1668 | 1668 | 16085с (4.47ч) | 93.90 | 103.29 | 206.58 |
| example_2.ctb | 28.9/0.05≈578 | 578 | 5250с (1.46ч) | 66.07 | 72.68 | 145.36 |
| example_3.ctb | 46.15/0.05≈923 | 923 | 8971с (2.49ч) | 43.41 | 47.75 | 95.50 |

## Не проверено / оставлено на будущее

- `cbddlp`/`ctb v2`/незашифрованный `ctb v4`/`.phz` — структуры и magic
  известны из открытых источников (см. ниже), но кода для них нет: нет ни
  одного реального файла для проверки. Добавляются веткой по `magic`, когда
  появится образец (см. `task.md`, раздел 6).
- Поля зашифрованного блока после `material_cost` (цвет смолы, имя машины,
  имя/тип смолы переменной длины — см. структуру `RESIN_PARAMETERS` в
  источниках) — не нужны для текущей задачи, не парсятся.
- Алгоритм `checksum` (расшифрованное поле на offset 0) неизвестен — не
  используется для валидации, только magic + границы файла.

## Источники

- [UVtools](https://github.com/sn4k3/UVtools) (MIT) — `ChituboxFile.cs`,
  `CTBEncryptedFile.cs`, `Scripts/010 Editor/ctb_encrypted.bt`,
  [discussion #750](https://github.com/sn4k3/UVtools/discussions/750)
  (magic-числа разных версий).
- [catibo](https://github.com/cbiffle/catibo) — независимая
  реверс-инжиниренная спецификация `cbddlp`/`ctb` (обычный, незашифрованный
  вариант) — `doc/cbddlp-ctb.adoc`.
