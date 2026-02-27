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

def get_charcs():
    # NM 296462523 is "Браслеты", subjectID 201
    url = 'https://content-api.wildberries.ru/content/v2/object/charcs/by-category?subjectID=201'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json().get('data', [])
        print(f"Fetched {len(data)} characteristics for subject 201.")
        # Look for weight
        for c in data:
            if 'Вес' in c.get('name', ''):
                print(f"Found Weight characteristic: {c}")
        
        with open('charcs_201_dump.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    get_charcs()
