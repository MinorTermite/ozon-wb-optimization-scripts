import json
import os
import requests
from datetime import datetime, timedelta

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load API key
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

def fetch_feedbacks():
    print("Fetching feedbacks...")
    # Using the feedback-api endpoint
    url = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
    params = {
        'isAnswered': 'true',
        'take': 1000,
        'skip': 0,
        'order': 'dateDesc'
    }
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json().get('data', {}).get('feedbacks', [])
            # Save raw for debug
            raw_path = os.path.join(ANALYTICS_DIR, 'raw_feedbacks.json')
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        else:
            print(f"Error fetching feedbacks: {r.status_code} {r.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

def analyze_feedbacks(feedbacks):
    low_rating = [f for f in feedbacks if f.get('productValuation', 5) <= 3]
    print(f"Total feedbacks: {len(feedbacks)}")
    print(f"Negative/Neutral feedbacks (<=3 stars): {len(low_rating)}")
    
    report = []
    for f in feedbacks:
        rating = f.get('productValuation', 5)
        if rating > 3:
            continue
            
        details = f.get('productDetails', {})
        nm_id = details.get('nmId')
        article = details.get('supplierArticle')
        prod_name = details.get('productName')
        
        report.append({
            'nmId': nm_id,
            'article': article,
            'prod_name': prod_name,
            'rating': rating,
            'text': f.get('text'),
            'answer': f.get('answer', {}).get('text') if f.get('answer') else 'No answer',
            'date': f.get('createdDate')
        })
    
    # Save to analytics
    output_path = os.path.join(ANALYTICS_DIR, 'wb_negative_reviews.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Generate markdown summary
    summary_path = os.path.join(ANALYTICS_DIR, 'low_rating_cards.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Анализ негативных отзывов\n\n")
        if not report:
            f.write("Негативных отзывов (<=3 звезд) не обнаружено.\n")
        else:
            f.write(f"Найдено {len(report)} отзывов с рейтингом 3 и ниже.\n\n")
            for item in report:
                f.write(f"### NM: {item['nmId']} | Рейтинг: {item['rating']}\n")
                f.write(f"**Дата:** {item['date']}\n")
                f.write(f"**Текст:** {item['text']}\n")
                f.write(f"**Ответ:** {item['answer']}\n")
                f.write("---\n")
    
    print(f"Report saved to {summary_path}")

if __name__ == "__main__":
    feedbacks = fetch_feedbacks()
    if feedbacks:
        analyze_feedbacks(feedbacks)
    else:
        print("No feedbacks found or error occurred.")
