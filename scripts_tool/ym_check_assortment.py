"""
Get active offers from Yandex Market Campaign using POST /campaigns/{CAMPAIGN_ID}/offers/all
"""
import requests, json

API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
BUSINESS_ID = 216491430
CAMPAIGN_ID = 148862812

BASE_URL = "https://api.partner.market.yandex.ru"
headers = {
    "Api-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_assortment():
    url = f"{BASE_URL}/campaigns/{CAMPAIGN_ID}/offers/all"
    res = requests.post(url, headers=headers, json={"limit": 200})
    if res.status_code != 200:
        print(f"Ошибка {res.status_code}: {res.text}")
        return []
    
    data = res.json()
    return data.get('result', {}).get('offers', [])

def main():
    print("=== АУДИТ АССОРТИМЕНТА ЯНДЕКС МАРКЕТА ===\n")
    offers = get_assortment()
    print(f"Найдено товаров: {len(offers)}")
    
    issues = []
    for off in offers:
        oid = off.get('offerId')
        pics = off.get('pictures', [])
        if len(pics) < 3:
            issues.append({'oid': oid, 'pics': pics})
            print(f"  ❌ [{oid}] фото: {len(pics)}")
            
    with open('ym_assortment.json', 'w', encoding='utf-8') as f:
        json.dump(offers, f, ensure_ascii=False, indent=2)
    
    if not issues:
        print("✅ У всех товаров 3+ фото")
    else:
        print(f"\nИтого проблемных товаров по фото: {len(issues)}")

if __name__ == "__main__":
    main()
