# Wibes Playbook

## Базовая логика

`Wibes` нельзя вести как каталог маркетплейса. Это короткий эмоциональный фид.

Рабочий принцип:
- первые `1-2` секунды должны быстро давать человеческий смысл;
- нельзя грузить ролик SEO-текстом;
- лучше один точный продуктовый ролик, чем десять нейросетевых фейков;
- нативные статьи должны греть интерес к подарку, а не прямолинейно продавать.

## Контентная очередь

Приоритетная family-first логика уже зафиксирована в:
- `obsidian/Wibes_Growth_OS_20260412/03_LAUNCH_QUEUE_20260412.md`

Сначала:
- дочери;
- сыну;
- семейные и парные сценарии;
- молитвы и защита;
- романтика;
- зодиак только в хвосте.

## Статус профиля

Подтверждено в:
- `output/playwright/wibes_profile_finalize_20260412.json`

Что уже сделано:
- установлен бренд `GravMix`
- установлен handle `@gravmix-gifts-ru`
- добавлен bio
- профиль приведен в нормальный вид

## Статья как нативный прогрев

Проверено, что в `Wibes` есть отдельный формат статей.

Скрипты:
- `scripts_tool/wibes_probe_create_options_20260412.js`
- `scripts_tool/wibes_probe_article_form_20260412.js`
- `scripts_tool/wibes_publish_article_20260412.js`

Подготовленные тексты:
- `obsidian/Wibes_Growth_OS_20260412/articles_native_20260412/01_podarok_rebenku_smysl_body.txt`
- `obsidian/Wibes_Growth_OS_20260412/articles_native_20260412/02_pochemu_bezlikie_podarki_body.txt`
- `obsidian/Wibes_Growth_OS_20260412/articles_native_20260412/03_chto_tseplyaet_silnee_tseny_body.txt`

## Публикация клипов

Скрипты:
- `scripts_tool/wibes_publish_generic_20260412.js`
- `scripts_tool/wibes_publish_939855999_20260412.js`

Скрипты по чистке:
- `scripts_tool/wibes_delete_all_clips_20260412.js`
- `scripts_tool/wibes_probe_delete_by_mouse_20260412.js`
- `scripts_tool/wibes_inspect_delete_ui_20260412.js`

Удаление использовать осторожно. Не запускать массовую зачистку без проверки текущего профиля.

## Лучший текущий ролик для SKU 939855999

Это не Gemini-видео, а exact-product motion из реальных stills.

Файлы:
- `obsidian/Wibes_Exact_Product_20260414/939855999_daughter_from_dad_exact/wibes_exact_product_939855999_20260414.mp4`
- `obsidian/Wibes_Exact_Product_20260414/939855999_daughter_from_dad_exact/wibes_exact_product_939855999_20260414_poster.png`
- `obsidian/Wibes_Exact_Product_20260414/939855999_daughter_from_dad_exact/wibes_exact_product_939855999_20260414.json`

Сборщик:
- `scripts_tool/build_wibes_exact_product_motion_939855999_20260414.py`

Почему этот ролик важен:
- использует только реальные фото браслета;
- не подменяет изделие;
- не ломает гравировку;
- подходит как безопасная база для публикации в `Wibes`.

## Практический стандарт на следующие ролики

Для новых SKU делать так:
1. собрать safe/crisp still pack из реальных фото;
2. проверить читаемость пластины;
3. собрать motion локально;
4. только после этого грузить в `Wibes`.

Не делать:
- пустые слайды;
- бессмысленные анимации ради анимации;
- нейросетевой фейк, если он уводит форму браслета;
- клипы, где изделие уже не похоже на реальный SKU.
