import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def check_good_card():
    # Get all cards
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    payload = {
        "settings": {
            "cursor": {
                "limit": 10
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }
    r = requests.post(url, headers=H, json=payload)
    if r.status_code == 200:
        cards = r.json().get('data', {}).get('cards', [])
        if cards:
            card = cards[0]
            print(f"Checking VC: {card['vendorCode']}")
            print("Characteristics:")
            print(json.dumps(card.get('characteristics', []), indent=2, ensure_ascii=False))
            print("Dimensions:")
            print(json.dumps(card.get('dimensions', {}), indent=2, ensure_ascii=False))
        else:
            print("No cards found.")
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    check_good_card()
