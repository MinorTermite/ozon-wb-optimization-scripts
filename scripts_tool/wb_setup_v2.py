# -*- coding: utf-8 -*-
"""
Test WB API connection with correct URLs
"""
import os
import requests
import json

env_path = '.env'
WB_KEY = ''
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('WB_API_KEY='):
            WB_KEY = line.strip().split('=', 1)[1]
            break

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

print('\nTesting WB Content API (Cards list)...')
try:
    # Use the standard content API URL
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json={
        'settings': {'cursor': {'limit': 10}, 'filter': {'withPhoto': -1}}
    }, timeout=30)
    if r.status_code == 200:
        data = r.json()
        cards = data.get('cards', [])
        print(f'SUCCESS! Found {len(cards)} items.')
        if cards:
            print(f'First item title: {cards[0].get("title", "")}')
            print(f'Available fields: {list(cards[0].keys())}')
    else:
        print(f'ERROR: {r.status_code} {r.text[:200]}')
except Exception as e:
    print(f'ERROR Content API: {e}')

print('\nTesting WB Adv API (Ad campaigns count)...')
try:
    r_adv = requests.get('https://advert-api.wildberries.ru/adv/v1/promotion/count', headers=headers, timeout=30)
    if r_adv.status_code == 200:
        print(f'SUCCESS Adv API: {r_adv.text}')
    else:
        print(f'ERROR Adv API: {r_adv.status_code} {r_adv.text[:200]}')
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
    else:
        print(f'ERROR Stat API: {r_stat.status_code} {r_stat.text[:200]}')
except Exception as e:
    print(f'ERROR Stat API Request: {e}')
