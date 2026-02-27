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

def test_endpoints():
    endpoints = [
        'https://content-api.wildberries.ru/content/v2/object/charcs/by-category?subjectID=201',
        'https://content-api.wildberries.ru/content/v1/object/characteristics?subjectId=201',
        'https://content-api.wildberries.ru/content/v2/directory/subjects?subjectID=201'
    ]
    
    for url in endpoints:
        print(f"Testing {url}...")
        r = requests.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Success!")
            # print(json.dumps(r.json(), ensure_ascii=False)[:500])
        else:
            print(f"Error: {r.text}")

if __name__ == "__main__":
    test_endpoints()
