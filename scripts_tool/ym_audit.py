"""
Yandex Market Partner API — full audit of all offers and their photos.
Business ID: 216491430
Campaign ID: 148862812
API Key: ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf
"""
import requests, json

API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
BUSINESS_ID = 216491430
CAMPAIGN_ID = 148862812

BASE_URL = "https://api.partner.market.yandex.ru"
headers = {
    "Authorization": f"Api-Key {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_connection():
    """Test API connection."""
    url = f"{BASE_URL}/businesses/{BUSINESS_ID}/offer-cards"
    res = requests.post(url, headers=headers, json={"limit": 1})
    print(f"\nТест подключения: {res.status_code}")
    if res.status_code != 200:
        print(f"Ответ: {res.text[:300]}")
    else:
        print("✅ API подключение работает!")
    return res.status_code == 200

def get_all_offer_cards():
    """Get all offer cards with photos."""
    url = f"{BASE_URL}/businesses/{BUSINESS_ID}/offer-cards"
    all_cards = []
    page_token = None
    
    while True:
        payload = {"limit": 200}
        if page_token:
            payload["page_token"] = page_token
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Ошибка получения карточек: {res.status_code} — {res.text[:200]}")
            break
        
        data = res.json()
        result = data.get('result', {})
        cards = result.get('offerCards', [])
        all_cards.extend(cards)
        
        paging = result.get('paging', {})
        next_page = paging.get('nextPageToken')
        
        print(f"  Загружено: {len(all_cards)} карточек...")
        
        if not next_page:
            break
        page_token = next_page
    
    return all_cards

def main():
    print("=== YANDEX MARKET PHOTO AUDIT ===")
    
    if not test_connection():
        # Try alternative auth format
        print("\nПробую альтернативный формат авторизации...")
        global headers
        headers["Authorization"] = f"Bearer {API_KEY}"
        if not test_connection():
            print("❌ API недоступен. Проверьте ключ.")
            return
    
    print("\nПолучаю все карточки товаров...")
    cards = get_all_offer_cards()
    print(f"Всего карточек: {len(cards)}")
    
    if not cards:
        print("Карточек не найдено")
        return
    
    # Analyze photos
    no_photos = []
    few_photos = []   # < 3 photos
    ok_photos = []
    
    for card in cards:
        offer_id = card.get('offerId', '')
        pictures = card.get('pictures', [])
        name = card.get('cardStatus', '')
        
        if len(pictures) == 0:
            no_photos.append({'offer_id': offer_id, 'name': name})
        elif len(pictures) < 3:
            few_photos.append({'offer_id': offer_id, 'count': len(pictures), 'pics': pictures})
        else:
            ok_photos.append({'offer_id': offer_id, 'count': len(pictures)})
    
    print(f"\n=== РЕЗУЛЬТАТ АУДИТА ФОТО ===")
    print(f"  ✅ Нормальные (≥3 фото): {len(ok_photos)}")
    print(f"  ⚠️ Мало фото (1-2):      {len(few_photos)}")
    print(f"  ❌ Без фото (0):          {len(no_photos)}")
    
    if no_photos:
        print(f"\nТовары без фото:")
        for item in no_photos[:20]:
            print(f"  [{item['offer_id']}] статус={item['name']}")
    
    if few_photos:
        print(f"\nТовары с малым кол-вом фото:")
        for item in few_photos[:10]:
            print(f"  [{item['offer_id']}] {item['count']} фото: {item['pics']}")
    
    # Save full cards data
    with open('ym_cards.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Полные данные сохранены в ym_cards.json")
    
    # Show structure of first card
    if cards:
        print(f"\n--- Структура карточки (первая) ---")
        print(json.dumps(cards[0], ensure_ascii=False, indent=2)[:800])

if __name__ == "__main__":
    main()
