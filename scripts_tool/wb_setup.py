# -*- coding: utf-8 -*-
"""
Save WB API key and test connection
"""
import os
import requests
import json

env_path = '.env'
WB_KEY = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzg3NzAxMjg5LCJmb3IiOiJzZWxmIiwiaWQiOiIwMTljOGY3NC00YjVkLTc1MDMtOWU0OS04M2EwODAzYjQ2NjAiLCJpaWQiOjM3ODQzMDAwLCJvaWQiOjEzMTg5MzcsInMiOjgxNjYyLCJzaWQiOiJlNDNhYTEzZC0yNjRjLTRhMzctOWEwZS04ZTQxYjIwYjI1OGUiLCJ0IjpmYWxzZSwidWlkIjozNzg0MzAwMH0.wjLopEd-XiFftsZ0fNgyzcF29zpYT6DWp0OBQ4nWBbmNIPnj3ZDsqpGNndo2jH9_YJBDBou0YYrtj2IwsxMA6w'

lines = []
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

has_wb = False
for i, line in enumerate(lines):
    if line.startswith('WB_API_KEY='):
        lines[i] = f'WB_API_KEY={WB_KEY}\n'
        has_wb = True
        break

if not has_wb:
    lines.append(f'\nWB_API_KEY={WB_KEY}\n')

with open(env_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Added WB_API_KEY to .env')

# Test WB API
headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

print('\nTesting WB Content API (Cards list)...')
r = requests.post('https://suppliers-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json={
    'settings': {'cursor': {'limit': 10}, 'filter': {'withPhoto': -1}}
}, timeout=30)
if r.status_code == 200:
    data = r.json()
    cards = data.get('cards', [])
    print(f'SUCCESS! Found {len(cards)} items in this page.')
    if cards:
        first_title = cards[0].get('title', '')
        print(f'First item title: {first_title}')
else:
    print(f'ERROR: {r.status_code} {r.text[:100]}')

print('\nTesting WB Adv API (Ad campaigns count)...')
try:
    r_adv = requests.get('https://advert-api.wildberries.ru/adv/v1/promotion/count', headers=headers, timeout=30)
    if r_adv.status_code == 200:
        print(f'SUCCESS Adv API: {r_adv.text}')
    elif r_adv.status_code == 401:
        print(f'UNAUTHORIZED Adv API: {r_adv.text[:100]} (Token might not have "Продвижение" permission)')
    else:
        print(f'ERROR Adv API: {r_adv.status_code} {r_adv.text[:100]}')
except Exception as e:
    print(f'ERROR Adv API Request: {e}')

print('\nTesting WB Statistics API (Sales)...')
try:
    import datetime
    date_from = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    r_stat = requests.get(f'https://statistics-api.wildberries.ru/api/v1/supplier/sales?dateFrom={date_from}', headers=headers, timeout=30)
    if r_stat.status_code == 200:
        sales = r_stat.json()
        print(f'SUCCESS Stat API: Found {len(sales)} sales in last 7 days')
    elif r_stat.status_code == 401:
        print(f'UNAUTHORIZED Stat API: {r_stat.text[:100]} (Token might not have "Статистика" permission)')
    else:
        print(f'ERROR Stat API: {r_stat.status_code} {r_stat.text[:100]}')
except Exception as e:
    print(f'ERROR Stat API Request: {e}')
