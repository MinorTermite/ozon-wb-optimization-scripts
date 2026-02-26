"""
RESTORE PHOTOS TO YANDEX MARKET.
1. Get healthy photo URLs from Ozon API.
2. Push them to Yandex Market Partner API (Card content update).
"""
import requests, json, time

# API Config Ozon
OZON_CLIENT_ID = "1537021" # From previous logs/env
OZON_API_KEY = "6901869e-d31e-450b-8d59-36657c9635b7" # From previous logs/env
o_headers = {'Client-Id': OZON_CLIENT_ID, 'Api-Key': OZON_API_KEY, 'Content-Type': 'application/json'}

# API Config Yandex
YM_API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
YM_BUSINESS_ID = 216491430
y_headers = {"Api-Key": YM_API_KEY, "Content-Type": "application/json"}

def get_ozon_photos():
    """Fetch all products and their images from Ozon."""
    url_list = "https://api-seller.ozon.ru/v3/product/list"
    offer_ids = []
    last_id = ""
    while True:
        res = requests.post(url_list, headers=o_headers, json={"filter": {"visibility": "ALL"}, "last_id": last_id, "limit": 100})
        data = res.json().get('result', {})
        items = data.get('items', [])
        for item in items:
            offer_ids.append(item.get('offer_id', ''))
        last_id = data.get('last_id', "")
        if not last_id or len(items) < 100: break
    
    url_info = "https://api-seller.ozon.ru/v3/product/info/list"
    photos_map = {}
    for i in range(0, len(offer_ids), 100):
        chunk = offer_ids[i:i+100]
        res = requests.post(url_info, headers=o_headers, json={"offer_id": chunk})
        items = res.json().get('items', []) or res.json().get('result', {}).get('items', [])
        for p in items:
            oid = p.get('offer_id')
            primary = str(p.get('primary_image', '')).strip("[]'\" ")
            gallery = p.get('images', [])
            all_pics = []
            if primary: all_pics.append(primary)
            for img in gallery:
                img_clean = str(img).strip("[]'\" ")
                if img_clean and img_clean not in all_pics:
                    all_pics.append(img_clean)
            photos_map[oid] = all_pics
    return photos_map

def update_ym_photos(offer_id, pictures):
    """Update Yandex Market card with photos."""
    url = f"https://api-partner.market.yandex.ru/businesses/{YM_BUSINESS_ID}/offer-cards/update"
    payload = {
        "offers": [
            {
                "offerId": offer_id,
                "pictures": pictures
            }
        ]
    }
    res = requests.post(url, headers=y_headers, json=payload)
    return res.status_code, res.text

def main():
    print("=== ВОССТАНОВЛЕНИЕ ФОТО: OZON -> YANDEX ===\n")
    
    print("1. Получаю фото из Ozon...")
    ozon_map = get_ozon_photos()
    print(f"   Найдено в Ozon: {len(ozon_map)} товаров с фото")
    
    # Get Yandex assortment to check what needs fix
    print("\n2. Получаю список товаров из Яндекс Маркета...")
    url_ym = f"https://api-partner.market.yandex.ru/campaigns/148862812/offers"
    res = requests.post(url_ym, headers=y_headers, json={"limit": 500})
    ym_offers = res.json().get('result', {}).get('offers', [])
    print(f"   Найдено в Яндексе: {len(ym_offers)} товаров")
    
    # Process
    restored = 0
    skipped = 0
    failed = 0
    
    items_to_fix = []
    for off in ym_offers:
        oid = off.get('offerId')
        existing_pics = off.get('pictures', [])
        
        # If no photos or only 1, try to restore from Ozon
        if len(existing_pics) < 2 and oid in ozon_map:
            new_pics = ozon_map[oid]
            if len(new_pics) > 0:
                items_to_fix.append((oid, new_pics))
    
    print(f"\n3. Найдено для восстановления: {len(items_to_fix)} товаров")
    
    # Batch update Yandex
    # The API /offer-cards/update accepts up to 20 offers per request
    for i in range(0, len(items_to_fix), 20):
        chunk = items_to_fix[i:i+20]
        payload = {
            "offers": [{"offerId": oid, "pictures": pics} for oid, pics in chunk]
        }
        url = f"https://api-partner.market.yandex.ru/businesses/{YM_BUSINESS_ID}/offer-cards/update"
        res = requests.post(url, headers=y_headers, json=payload)
        
        if res.status_code == 200:
            restored += len(chunk)
            print(f"   ✅ Батч {i//20+1}: +{len(chunk)} товаров")
        else:
            failed += len(chunk)
            print(f"   ❌ Батч {i//20+1}: ошибка {res.status_code} - {res.text[:200]}")
        
        time.sleep(1) # Rate limiting
        
    print(f"\nИТОГ:")
    print(f"  ✅ Восстановлено: {restored}")
    print(f"  ❌ Ошибок:       {failed}")

if __name__ == "__main__":
    main()
