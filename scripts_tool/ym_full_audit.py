"""
Full Yandex Market photo audit using correct Api-Key header format.
Gets all offer cards, checks photos, identifies issues.
"""
import requests, json

API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
BUSINESS_ID = 216491430

BASE_URL = "https://api.partner.market.yandex.ru"
headers = {
    "Api-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_all_offer_cards():
    url = f"{BASE_URL}/businesses/{BUSINESS_ID}/offer-cards"
    all_cards = []
    page_token = None
    
    while True:
        payload = {"limit": 200}
        if page_token:
            payload["page_token"] = page_token
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Ошибка: {res.status_code} — {res.text[:200]}")
            break
        
        data = res.json()
        result = data.get('result', {})
        cards = result.get('offerCards', [])
        all_cards.extend(cards)
        
        paging = result.get('paging', {})
        next_page = paging.get('nextPageToken')
        
        print(f"  Загружено: {len(all_cards)} карточек...")
        
        if not next_page or len(cards) == 0:
            break
        page_token = next_page
    
    return all_cards

def main():
    print("=== YANDEX MARKET PHOTO AUDIT ===\n")
    
    print("Загружаю все карточки...")
    cards = get_all_offer_cards()
    print(f"Всего карточек: {len(cards)}\n")
    
    if not cards:
        return
    
    # Analyze
    no_photos = []
    few_photos = []     # 1-2 photos
    ok_photos = []      # 3+ photos
    
    for card in cards:
        offer_id = card.get('offerId', '')
        pictures = card.get('pictures', [])
        card_status = card.get('cardStatus', '')
        errors = card.get('errors', [])
        warnings = card.get('warnings', [])
        
        photo_count = len(pictures)
        
        if photo_count == 0:
            no_photos.append({
                'offer_id': offer_id,
                'card_status': card_status,
                'errors': errors,
                'warnings': warnings
            })
        elif photo_count < 3:
            few_photos.append({
                'offer_id': offer_id,
                'count': photo_count,
                'pictures': pictures,
                'card_status': card_status
            })
        else:
            ok_photos.append({'offer_id': offer_id, 'count': photo_count})
    
    print(f"{'='*60}")
    print(f"📊 АУДИТ ФОТО")
    print(f"{'='*60}")
    print(f"  ✅ Хорошо (≥3 фото): {len(ok_photos)}")
    print(f"  ⚠️ Мало (1-2 фото):  {len(few_photos)}")
    print(f"  ❌ Нет фото:         {len(no_photos)}")
    
    if no_photos:
        print(f"\n❌ ТОВАРЫ БЕЗ ФОТО ({len(no_photos)}):")
        for item in no_photos:
            print(f"  [{item['offer_id']}] статус={item['card_status']}")
            if item['errors']:
                print(f"    ошибки: {item['errors'][:2]}")
    
    if few_photos:
        print(f"\n⚠️ ТОВАРЫ С МАЛО ФОТО ({len(few_photos)}):")
        for item in few_photos:
            print(f"  [{item['offer_id']}] {item['count']} фото | статус={item['card_status']}")
            for pic in item['pictures']:
                url_pic = pic.get('url', pic) if isinstance(pic, dict) else pic
                print(f"    - {url_pic}")
    
    # Show card structure
    print(f"\n--- Пример структуры карточки ---")
    print(json.dumps(cards[0], ensure_ascii=False, indent=2)[:1000])
    
    # Save full data
    with open('ym_cards_full.json', 'w', encoding='utf-8') as f:
        json.dump({
            'cards': cards,
            'no_photos': no_photos,
            'few_photos': few_photos
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Данные сохранены в ym_cards_full.json")
    
    return {'no_photos': no_photos, 'few_photos': few_photos, 'ok': ok_photos}

if __name__ == "__main__":
    main()
