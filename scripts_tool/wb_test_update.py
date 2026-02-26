# -*- coding: utf-8 -*-
"""
Test WB card update - single card with actual change
"""
import requests, json

with open('.env', 'r', encoding='utf-8') as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

# Load a SHORT description card
with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Find one with short desc
short = [c for c in cards if 0 < len(c.get('description', '')) < 500]
c = short[0]
nmID = c['nmID']
vc = c['vendorCode']
old_desc = c['description']
title = c['title']

print("Card:", nmID, vc)
print("Title:", title)
print("Old desc length:", len(old_desc))

# Generate expanded description
new_desc = old_desc + " Изделие выполнено из высококачественной нержавеющей стали 316L, которая не темнеет, не ржавеет и не вызывает аллергических реакций. Универсальный размер подойдет как мужчинам, так и женщинам. Поставляется в подарочной упаковке — бархатном мешочке, полностью готов к вручению. Отличный подарок на день рождения, 23 февраля, 8 марта или просто как знак внимания без повода. Бренд GRAVMIX гарантирует долговечность и премиальное качество каждого изделия."

print("New desc length:", len(new_desc))

# Try update
body = [{"nmID": nmID, "vendorCode": vc, "description": new_desc}]
r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
print("Result:", r.status_code)
print("Response:", r.text[:300])
