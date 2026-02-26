import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def test_format(card, char_id, char_name, char_val, label):
    print(f"\n--- Testing Format: {label} ({repr(char_val)}) ---")
    
    body = [{
        "nmID": card['nmID'],
        "vendorCode": card['vendorCode'],
        "characteristics": [
            {
                "id": char_id,
                "name": char_name,
                "value": char_val
            }
        ],
        "dimensions": {
            "width": 5,
            "height": 2,
            "length": 5,
            "weightBrutto": 0.05
        }
    }]
    
    url = "https://content-api.wildberries.ru/content/v2/cards/update"
    r = requests.post(url, headers=H, json=body)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    # Find a card with 'Ширина предмета' or 'Длина предмета'
    target_card = None
    target_char = None
    for c in cards:
        for ch in c.get('characteristics', []):
            if ch['name'] in ['Ширина предмета', 'Длина предмета']:
                target_card = c
                target_char = ch
                break
        if target_card: break

    if not target_card:
        print("Required characteristic not found in dump!")
        exit(1)

    print(f"Using Card: {target_card['vendorCode']} (nmID: {target_card['nmID']})")
    print(f"Testing char: {target_char['name']} (ID: {target_char['id']})")

    # The four horsemen of WB numeric types
    test_format(target_card, target_char['id'], target_char['name'], ["5"], "List of Strings")
    test_format(target_card, target_char['id'], target_char['name'], [5], "List of Ints")
    test_format(target_card, target_char['id'], target_char['name'], 5, "Single Int")
    test_format(target_card, target_char['id'], target_char['name'], "5", "Single String")
