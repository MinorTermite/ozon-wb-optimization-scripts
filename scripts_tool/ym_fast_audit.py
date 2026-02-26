"""
Fast Yandex Market Audit focusing ONLY on the 120 active offers in the campaign.
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
    all_offers = []
    page_token = None
    
    while True:
        res = requests.get(url, headers=headers, params={"limit": 500, "page_token": page_token})
        if res.status_code != 200:
            print(f"Ошибка: {res.status_code} — {res.text[:200]}")
            break
        
        data = res.json()
        result = data.get('result', {})
        offers = result.get('offers', [])
        all_offers.extend(offers)
        
        paging = result.get('paging', {})
        next_page = paging.get('nextPageToken')
        
        if not next_page:
            break
        page_token = next_page
    
    return all_offers

def main():
    print("=== БЫСТРЫЙ АУДИТ ЯНДЕКС МАРКЕТА (Активные товары) ===\n")
    
    offers = get_campaign_offers()
    print(f"Найдено активных товаров в магазине: {len(offers)}")
    
    if not offers:
        return

    # Check for photo issues
    no_photos = []
    few_photos = [] # < 2
    
    for off in offers:
        oid = off.get('offerId')
        pics = off.get('pictures', [])
        if not pics:
            no_photos.append(oid)
        elif len(pics) < 2:
            few_photos.append((oid, pics))

    print(f"  ❌ Без фото: {len(no_photos)}")
    print(f"  ⚠️ 1 фото:    {len(few_photos)}")
    
    if no_photos:
        print(f"\nАртикулы без фото: {no_photos}")
    
    # Save results
    with open('ym_active_audit.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(offers),
            'no_photos': no_photos,
            'few_photos': few_photos,
            'offers_sample': offers[:10]
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
