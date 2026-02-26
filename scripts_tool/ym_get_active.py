"""
Get 120 active offers from Yandex Market Campaign using POST /campaigns/{CAMPAIGN_ID}/offers
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

def get_campaign_offers():
    url = f"{BASE_URL}/campaigns/{CAMPAIGN_ID}/offers"
    res = requests.post(url, headers=headers, json={"limit": 500})
    if res.status_code != 200:
        print(f"Ошибка {res.status_code}: {res.text}")
        return []
    
    data = res.json()
    return data.get('result', {}).get('offers', [])

def main():
    print("=== ПОЛУЧЕНИЕ 120 ТОВАРОВ ЯНДЕКС МАРКЕТА ===\n")
    offers = get_campaign_offers()
    print(f"Найдено товаров: {len(offers)}")
    
    if not offers:
        print("Список пуст.")
        return

    # Filter by GravMix articuls (they usually start with 'брас' or contain specific codes)
    # But user says they have 120 items total.
    
    no_photos = []
    for off in offers:
        oid = off.get('offerId')
        pics = off.get('pictures', [])
        if not pics:
            no_photos.append(oid)
            
    print(f"Товаров без фото: {len(no_photos)}")
    if no_photos:
        print(f"Артикулы: {no_photos}")

    with open('ym_active_offers.json', 'w', encoding='utf-8') as f:
        json.dump(offers, f, ensure_ascii=False, indent=2)
    print("\n✅ Сохранено в ym_active_offers.json")

if __name__ == "__main__":
    main()
