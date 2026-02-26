# -*- coding: utf-8 -*-
import json

try:
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    no_desc = sum(1 for c in cards if not c.get('description'))
    short_desc = sum(1 for c in cards if 0 < len(c.get('description', '')) < 500)
    good_desc = sum(1 for c in cards if 500 <= len(c.get('description', '')) <= 2000)
    long_desc = sum(1 for c in cards if len(c.get('description', '')) > 2000)
    bad_chars = sum(1 for c in cards if len(c.get('characteristics', [])) < 5)
    avg_len = sum(len(c.get('description', '')) for c in cards) / max(1, len(cards))

    out = f"""
Всего карточек: {len(cards)}

ДЛИНА ОПИСАНИЙ:
* Без описания: {no_desc}
* Короткие (< 500 симв): {short_desc}
* Нормальные (500-2000): {good_desc}
* Длинные (> 2000): {long_desc}
* Средняя длина: {avg_len:.0f} символов

ХАРАКТЕРИСТИКИ:
* Заполнено < 5 характеристик: {bad_chars} шт.
"""
    print(out)
except Exception as e:
    print(f"Error: {e}")
