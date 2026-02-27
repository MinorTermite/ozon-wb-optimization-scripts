import json
import os
import requests
import re
import time

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
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

def remove_emojis(text):
    if not text: return ""
    return re.sub(r'[^\x00-\x7f\u0400-\u04FF\s]', '', text).strip()

def expand_title(title, subject_name):
    # Add gift keywords if not present
    title = remove_emojis(title)
    if not title: return f"Подарок {subject_name} GRAVMIX"
    
    # We will be very conservative: 50 chars limit to avoid any hidden WB byte-count issues
    keywords = ["подарок", "сувенир", "для него", "для нее"]
    for kw in keywords:
        if kw.lower() not in title.lower() and len(title) + len(kw) + 1 < 45:
            title += f" {kw}"
    
    # Ensure brand is there
    if "GRAVMIX" not in title and "GravMix" not in title:
        if len(title) + 8 < 50:
            title += " GRAVMIX"
        else:
            title = title[:41] + " GRAVMIX"
    
    # Final safety cut
    return title[:50].strip()

def process_all_cards():
    if not os.path.exists(DATA_DUMP_PATH):
        print("Error: Data dump not found")
        return
        
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    print(f"Loaded {len(cards)} cards for ultimate optimization.")
    
    ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
    if not os.path.exists(ANALYTICS_DIR):
        os.makedirs(ANALYTICS_DIR)
        
    # Reset progress to re-optimize everything and fix drafts
    resume_path = os.path.join(ANALYTICS_DIR, 'optimizer_progress.txt')
    start_idx = 0
    
    # Force reset or allow manual override? Let's just reset for this fix.
    # with open(resume_path, 'w') as f: f.write("0")
    
    batch = []
    for i in range(start_idx, len(cards)):
        card = cards[i]
        nm_id = card.get('nmID')
        subj = card.get('subjectName', '')
        
        # Safety: skip cards that don't have nmID if any (clones are already handled)
        if not nm_id: continue

        new_title = expand_title(card.get('title', ''), subj)
        new_desc = remove_emojis(card.get('description', ''))
        
        new_characteristics = []
        for char in card.get('characteristics', []):
            if char.get('id') == 77 or char.get('name') == 'Бренд':
                new_characteristics.append({'id': 77, 'name': 'Бренд', 'value': ['GravMix']})
            else:
                new_characteristics.append(char)
        if not any(c.get('id') == 77 for c in new_characteristics):
            new_characteristics.append({'id': 77, 'name': 'Бренд', 'value': ['GravMix']})
            
        payload = {
            "nmID": nm_id,
            "vendorCode": card.get('vendorCode'),
            "title": new_title,
            "description": new_desc,
            "characteristics": new_characteristics,
            "dimensions": card.get('dimensions'),
            "sizes": card.get('sizes')
        }
        batch.append(payload)
        
        if len(batch) >= 10: # Balanced batch
            status = send_batch(batch)
            if status == 200:
                batch = []
                with open(resume_path, 'w') as wf:
                    wf.write(str(i + 1))
                time.sleep(1) # Faster but safe
            elif status == 429:
                print("Rate limit hit. Waiting 60s...")
                time.sleep(60)
                # Keep items in batch to retry
            else:
                print(f"Failed status {status}. Clearing batch and moving on.")
                batch = []
                time.sleep(2)
            
    if batch:
        send_batch(batch)
        with open(resume_path, 'w') as wf:
            wf.write(str(len(cards)))

def send_batch(batch):
    print(f"Updating batch of {len(batch)} items...")
    url = 'https://content-api.wildberries.ru/content/v2/cards/update'
    try:
        r = requests.post(url, headers=headers, json=batch, timeout=60)
        if r.status_code == 200:
            print(f"Batch updated successfully.")
            return 200
        else:
            print(f"Error updating batch: {r.status_code} {r.text}")
            return r.status_code
    except Exception as e:
        print(f"Exception during update: {e}")
        return 500

if __name__ == "__main__":
    process_all_cards()
