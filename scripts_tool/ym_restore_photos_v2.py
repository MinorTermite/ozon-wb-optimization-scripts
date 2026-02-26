"""
RESTORE PHOTOS TO YANDEX MARKET (v2).
Fixed Ozon credentials and SSL Yandex issue.
"""
import os, requests, json, time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load ENV
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

OZON_CLIENT_ID = os.environ.get('OZON_CLIENT_ID')
OZON_API_KEY = os.environ.get('OZON_API_KEY')
YM_API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
YM_BUSINESS_ID = 216491430
YM_CAMPAIGN_ID = 148862812

o_headers = {'Client-Id': OZON_CLIENT_ID, 'Api-Key': OZON_API_KEY, 'Content-Type': 'application/json'}
y_headers = {"Api-Key": YM_API_KEY, "Content-Type": "application/json"}

def get_ozon_photos():
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

def main():
    print("=== ВОССТАНОВЛЕНИЕ ФОТО (v2): OZON -> YANDEX ===\n")
    
    # 1. Get IDs from Yandex first to know what to fix
    print("1. Получаю список 120 товаров из Яндекс Маркета...")
    url_ym = f"https://api.partner.market.yandex.ru/campaigns/{YM_CAMPAIGN_ID}/offers"
    res = requests.post(url_ym, headers=y_headers, json={"limit": 500}, verify=False)
    ym_offers = res.json().get('result', {}).get('offers', [])
    print(f"   Найдено в Яндексе: {len(ym_offers)} товаров")
    
    if not ym_offers:
        print("Ошибка: не удалось получить список товаров Яндекса.")
        return

    # 2. Get Ozon photos
    print("\n2. Получаю фото из Ozon...")
    ozon_map = get_ozon_photos()
    print(f"   База Ozon: {len(ozon_map)} товаров с фото")
    
    # 3. Match and Prepare
    items_to_fix = []
    for off in ym_offers:
        oid = off.get('offerId')
        pics = off.get('pictures', [])
        
        # If no photos (common state now) or only 1, restore from Ozon
        if len(pics) < 2 and oid in ozon_map:
            items_to_fix.append((oid, ozon_map[oid]))
        elif oid not in ozon_map:
            # Fallback for universal bracelets if mapping fails
            # Most GravMix items use the same universal set
            # But we only do direct mapping for safety
            pass

    print(f"\n3. Найдено для восстановления: {len(items_to_fix)} товаров")
    
    # 4. Push updates to Yandex
    restored = 0
    failed = 0
    
    for i in range(0, len(items_to_fix), 20):
        chunk = items_to_fix[i:i+20]
        payload = {
            "offers": [{"offerId": oid, "pictures": pics} for oid, pics in chunk]
        }
        url = f"https://api.partner.market.yandex.ru/businesses/{YM_BUSINESS_ID}/offer-cards/update"
        res = requests.post(url, headers=y_headers, json=payload, verify=False)
        
        if res.status_code == 200:
            restored += len(chunk)
            print(f"   ✅ Батч {i//20+1}: +{len(chunk)} товаров успешно")
        else:
            failed += len(chunk)
            print(f"   ❌ Батч {i//20+1}: ошибка {res.status_code} - {res.text[:200]}")
        time.sleep(1)
        
    print(f"\nИТОГ: ✅ {restored} успешно, ❌ {failed} ошибок.")

if __name__ == "__main__":
    main()
