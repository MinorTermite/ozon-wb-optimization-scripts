import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def study_card():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    payload = {'settings': {'cursor': {'limit': 5}, 'filter': {'withPhoto': -1}}}
    r = requests.post(url, headers=H, json=payload)
    if r.status_code == 200:
        cards = r.json().get('data', {}).get('cards', [])
        if not cards:
            print('No cards found')
            return
        
        for card in cards:
            print(f"\n--- Card {card['vendorCode']} ---")
            chars = card.get('characteristics', [])
            found_num = False
            for ch in chars:
                name = ch.get('name')
                val = ch.get('value')
                # Check for characteristics that are usually numeric
                if any(x in name for x in ['Ширина', 'Длина', 'Высота', 'Количество']):
                    v_type = type(val[0]).__name__ if val else 'None'
                    v_raw_type = type(val).__name__
                    print(f"Characteristic: {name}")
                    print(f"  Value: {repr(val)}")
                    print(f"  Container type: {v_raw_type}")
                    print(f"  Element type: {v_type}")
                    found_num = True
            if not found_num:
                print("No numeric-looking characteristics found in this card.")
    else:
        print(f"Error: {r.status_code} {r.text}")

if __name__ == "__main__":
    study_card()
