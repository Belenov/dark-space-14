# Dark Space

Форк Space Station 14. Далёкая вселенная, где холодная война так и не закончилась:
социалистический Восток против капиталистического Запада. Лор опирается на советскую
космическую фантастику и космический хоррор.

## Remote

- `origin`: https://github.com/Belenov/dark-space-14 (наш форк)
- `upstream`: https://github.com/space-wizards/space-station-14 (оригинал)

Обновление из апстрима: `git fetch upstream && git merge upstream/master`.

## Где лежит наш контент

Всё своё кладём в папки `_DarkSpace`, чтобы не конфликтовать с апстримом при мерджах:

- `Resources/Prototypes/_DarkSpace/` — прототипы (YAML)
- `Resources/Textures/_DarkSpace/` — спрайты (RSI)
- `Resources/Audio/_DarkSpace/` — звуки
- `Resources/Locale/<lang>/_DarkSpace/` — локализация (FTL)
- `Content.{Server,Client,Shared}/_DarkSpace/` — код (namespace `Content.*._DarkSpace`)

Если приходится менять файл апстрима, помечаем правку комментарием `// DarkSpace` (в YAML `# DarkSpace`).

## Конфиг сервера

Пресет: `Resources/ConfigPresets/DarkSpace/main.toml`. Включается строкой
`config.presets = "DarkSpace/main"` в секции `[config]` файла `server_config.toml`.
