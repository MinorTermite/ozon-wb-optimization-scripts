import requests
import json
import os

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

def check_subjects_and_v3():
    # 1. Fetch subjects
    print("Fetching valid subjects...")
    r = requests.get('https://content-api.wildberries.ru/content/v2/object/all?limit=1000', headers=headers)
    if r.status_code == 200:
        subjects = r.json().get('data', [])
        # Save a few for reference
        with open('subjects_dump.json', 'w', encoding='utf-8') as f:
            json.dump(subjects, f, ensure_ascii=False, indent=2)
        print(f"Fetched {len(subjects)} subjects.")
    
    # 2. Try one card with _v3
    print("\nAttempting one card with _v3 suffix to test 'upload'...")
    # Using data from first card in cards_seo_dump.json (NM 296462523, Браслеты)
    # Based on Step 910: subjectID 201
    
    payload = [{
        "subjectID": 201,
        "variants": [{
            "vendorCode": "test_recreate_v3",
            "brand": "GravMix",
            "title": "Тестовый браслет V3",
            "description": "Описание тестового браслета",
            "dimensions": {
                "width": 10,
                "height": 2,
                "length": 15
            },
            "characteristics": [
                 {"name": "Цвет", "value": ["серебристый"]}
            ],
            "sizes": [
                {
                    "techSize": "0",
                    "wbSize": "",
                    "skus": []
                }
            ],
            "mediaFiles": ["https://basket-18.wbbasket.ru/vol2964/part296462/296462523/images/big/1.webp"]
        }]
    }]
    
    r = requests.post('https://content-api.wildberries.ru/content/v2/cards/upload', headers=headers, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    check_subjects_and_v3()
