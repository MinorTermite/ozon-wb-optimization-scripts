"""
RESTORE PHOTOS TO YANDEX MARKET (v4).
Using "offer-mappings/update" endpoint - specifically for simple updates like photos.
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
        for item in items: offer_ids.append(item.get('offer_id', ''))
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
            all_pics = [primary] + [str(img).strip("[]'\" ") for img in gallery if str(img).strip("[]'\" ") != primary]
            photos_map[oid] = [url for url in all_pics if url]
    return photos_map

def main():
    print("=== ВОССТАНОВЛЕНИЕ ФОТО (v4): OZON -> YANDEX (OFFER-MAPPINGS) ===\n")
    
    print("1. Получаю список 120 товаров из Яндекс Маркета...")
    url_ym = f"https://api.partner.market.yandex.ru/campaigns/{YM_CAMPAIGN_ID}/offers"
    res = requests.post(url_ym, headers=y_headers, json={"limit": 500}, verify=False)
    ym_offers = res.json().get('result', {}).get('offers', [])
    print(f"   Найдено в Яндексе: {len(ym_offers)} товаров")
    
    print("\n2. Получаю фото из Ozon...")
    ozon_map = get_ozon_photos()
    
    items_to_fix = []
    for off in ym_offers:
        oid = off.get('offerId')
        # Even if photos exist, user said "restore deleted", so we push Ozon versions to be sure
        if oid in ozon_map:
            items_to_fix.append({"offer": {"offerId": oid, "pictures": ozon_map[oid]}})

    print(f"\n3. Найдено для восстановления: {len(items_to_fix)} товаров")
    
    if not items_to_fix:
        print("Ничего не найдено для исправления.")
        return

    # Update Yandex via offer-mappings/update
    # Max batch size for this endpoint is usually 200, we use 50
    for i in range(0, len(items_to_fix), 50):
        chunk = items_to_fix[i:i+50]
        payload = {"offerMappings": chunk}
        url = f"https://api.partner.market.yandex.ru/businesses/{YM_BUSINESS_ID}/offer-mappings/update"
        res = requests.post(url, headers=y_headers, json=payload, verify=False)
        
        if res.status_code == 200:
            print(f"   ✅ Батч {i//50+1}: +{len(chunk)} товаров успешно")
        else:
            print(f"   ❌ Батч {i//50+1}: ошибка {res.status_code} - {res.text[:300]}")
        time.sleep(1)

if __name__ == "__main__":
    main()
