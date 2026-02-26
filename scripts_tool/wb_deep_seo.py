import json
import requests
import time
import random

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

STRICT_NUMERIC = ['Ширина упаковки', 'Высота упаковки', 'Длина упаковки', 'Высота предмета', 'Ширина предмета']

def detect_zodiac(text):
    signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    import re
    t_low = text.lower()
    for s in signs:
        if re.search(r'\b' + s.lower()[:3] + r'[а-я]*\b', t_low):
            # Special case for 'Рак' to avoid matching inside other short words if not careful, 
            # actually just searching exact word or root is safer:
            pass
        # Better naive approach:
        if s.lower() in t_low.split(): return s
        if re.search(r'\b' + s.lower() + r'\b', t_low): return s
        if s == 'Близнецы' and re.search(r'\bблизнец[а-я]*\b', t_low): return s
        if s == 'Дева' and re.search(r'\bдев[уы]\b', t_low): return s
        if s == 'Рыбы' and re.search(r'\bрыб[уы]\b', t_low): return s
        if s == 'Рак' and re.search(r'\bрак[ауомe]?\b', t_low): return s
        if s == 'Весы' and re.search(r'\bвес[ауомeы]\b', t_low): return s
    return None

def generate_seo_title(title, subj_id):
    t_low = title.lower()
    zodiac = detect_zodiac(title)
    
    # Target: 60 chars max.
    if subj_id == 201: # Браслеты
        if zodiac:
            base = f"Браслет со знаком зодиака {zodiac} сталь GRAVMIX"
        elif 'муж' in t_low or 'пап' in t_low or 'сын' in t_low or 'брат' in t_low or 'дед' in t_low:
            base = f"{title} мужской сталь GRAVMIX"
        elif 'жен' in t_low or 'мам' in t_low or 'доч' in t_low or 'бабуш' in t_low or 'сестр' in t_low:
            base = f"{title} женский сталь GRAVMIX"
        elif 'парн' in t_low:
            base = f"Парные браслеты для двоих влюбленных сталь GRAVMIX"
        else:
            base = f"{title} металлический сталь GRAVMIX"
            
    elif subj_id == 297: # Брелоки
        if 'парн' in t_low:
            base = f"Парные брелоки для ключей подарок сталь GRAVMIX"
        elif 'авто' in t_low or 'машин' in t_low:
            base = f"Брелок для ключей автомобиля автобрелок сталь GRAVMIX"
        else:
            base = f"{title} брелок для ключей сталь GRAVMIX"
            
    else:
        base = f"{title} украшение сталь GRAVMIX"
        
    # Clean up multiple GRAVMIX or сталь
    base = base.replace('GRAVMIX GRAVMIX', 'GRAVMIX')
    base = base.replace('сталь сталь', 'сталь')
    
    # If still very short, add SEO words
    if len(base) < 40:
        base = (base + " в подарок").strip()
        
    return base[:60].strip()

def generate_seo_desc(title, subj_id):
    t_low = title.lower()
    zodiac = detect_zodiac(title)
    
    intro = f"Ищете идеальный подарок, который запомнится надолго? Представляем эксклюзивный аксессуар от российского бренда GRAVMIX — {title}. Это не просто украшение, это эмоция, запечатленная в металле."
    
    if subj_id == 201: # Браслет
        type_desc = "Стильный и минималистичный браслет выполнен в форме жесткого кольца (каффа), который легко адаптируется под размер вашей руки. Отсутствие сложных застежек делает его надежным и долговечным."
    else:
        type_desc = "Надежный брелок для ключей оснащен качественным кольцом и карабином, что гарантирует сохранность ваших ключей от дома или автомобиля."

    zodiac_text = ""
    if zodiac:
        zodiac_text = f" Астрологический символ '{zodiac}' превращает этот аксессуар в личный талисман и оберег, приносящий удачу своему владельцу. "

    material_desc = "Изделие изготовлено из премиальной ювелирной нержавеющей стали 316L. Этот материал превосходит серебро по практичности: он не темнеет со временем, не окисляется от воды или пота, не ржавеет и абсолютно гипоаллергенен. Вы можете носить его не снимая на тренировках, в душе или бассейне — гравировка не сотрется и не потускнеет."

    gift_desc = "Данный аксессуар станет потрясающим сюрпризом на любой праздник: День Рождения, Новый год, 14 февраля (День Святого Валентина), 23 февраля или 8 марта. Подарите его близкому человеку — любимому мужчине, мужу, парню, папе, брату, жене, маме, сестре, подруге или дочке."

    packing_desc = "Мы позаботились о том, чтобы ваш подарок выглядел престижно: каждый товар бережно упакован в фирменную крафтовую подарочную коробку с наполнителем. Вам не придется докупать упаковку!"

    seo_spam = "Теги для поиска: недорогие подарки, парные украшения для двоих влюбленных лп, стальные ювелирные изделия, аксессуары в машину, брелочек на ключи авто, жесткий металлический браслет с надписью надписями, оригинальный сувенир годовщину свадьбы отношений, памятный презент."

    full_text = f"{intro} {type_desc}{zodiac_text} {material_desc}\n\n{gift_desc}\n\n{packing_desc}\n\nО бренде: GRAVMIX — это собственное производство в России и строгий контроль качества на каждом этапе. Выбирайте надежность и стиль!\n\n{seo_spam}"
    
    # Ensure it's not too ridiculously long, limit to WB constraints if any, usually 5000 is fine, we hover around 1200
    return full_text

def get_gender(title):
    t_low = title.lower()
    if 'муж' in t_low or 'пап' in t_low or 'сын' in t_low or 'дед' in t_low or 'брат' in t_low:
        return 'Мужской'
    elif 'жен' in t_low or 'мам' in t_low or 'бабу' in t_low or 'доч' in t_low or 'сест' in t_low:
        return 'Женский'
    return 'Женский' # Default safe for jewelry

def apply_deep_seo():
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    updates = []
    
    for c in cards:
        orig_title = c.get('title', '')
        subj_id = c.get('subjectID')
        
        # 1. New Title
        new_title = generate_seo_title(orig_title, subj_id)
        
        # 2. New Description
        new_desc = generate_seo_desc(orig_title, subj_id)
        
        # 3. Handle Characteristics
        old_chars = c.get('characteristics', [])
        new_chars = []
        seen = set()
        
        for ch in old_chars:
            name = ch['name']
            val = ch['value']
            
            if name == 'Пол':
                new_val = get_gender(orig_title)
                new_chars.append({"id": ch['id'], "name": name, "value": [new_val]})
                seen.add(name)
                continue
                
            if name in STRICT_NUMERIC:
                try:
                    num_val = int(float(val[0])) if isinstance(val, list) and val else int(float(val))
                    new_chars.append({"id": ch['id'], "name": name, "value": num_val})
                except:
                    new_chars.append({"id": ch['id'], "name": name, "value": val})
            else:
                new_chars.append({"id": ch['id'], "name": name, "value": val})
            seen.add(name)

        # 4. Inject Missing SEO Fields
        seo_fields = {
            201: {
                'Повод': ['день рождения', '14 февраля', '8 марта'],
                'Назначение подарка': ['для мужчины', 'для женщины', 'любимому', 'любимой'],
                'Вид замка': ['без застежки'],
                'Вставка': ['без вставки'],
                'Особенности ювелирного изделия': ['алмазная гравировка'],
                'Материал ювелирного изделия': ['ювелирная сталь', 'сталь 316L']
            },
            297: {
                'Повод': ['день рождения', '23 февраля', '8 марта'],
                'Назначение подарка': ['для мужчины', 'для женщины', 'мужу', 'автовладельцу'],
                'Особенности брелока': ['металлический', 'с гравировкой'],
                'Материал изделия': ['сталь', 'металл']
            }
        }
        
        if subj_id in seo_fields:
            for fname, fvals in seo_fields[subj_id].items():
                if fname not in seen:
                    new_chars.append({"name": fname, "value": fvals})
        
        # Maintain mandatory dimensions blocks
        u = {
            "nmID": c['nmID'],
            "imtID": c['imtID'],
            "vendorCode": c['vendorCode'],
            "title": new_title,
            "description": new_desc,
            "characteristics": new_chars,
            "sizes": [
                {
                    "chrtID": c['sizes'][0]['chrtID'],
                    "wbSize": "", "price": 1000,
                    "skus": c['sizes'][0].get('skus', [])
                }
            ],
            "dimensions": { "length": 5, "width": 5, "height": 2, "weightBrutto": 0.05, "isValid": True }
        }
        updates.append(u)

    print(f"Prepared full SEO updates for {len(updates)} cards.")
    
    # Batch execute
    BATCH_SIZE = 50
    ok, err = 0, 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        try:
            r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=batch, timeout=30)
            if r.status_code == 429:
                print("  Got 429. Sleeping 60s...")
                time.sleep(60)
                r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=batch, timeout=30)
                
            if r.status_code == 200 and not r.json().get('error'):
                ok += len(batch)
                print(f"  Success batch {i//BATCH_SIZE + 1}. Progress: {min(i+BATCH_SIZE, len(updates))}/{len(updates)}")
            else:
                err += len(batch)
                print(f"  ERR batch {i//BATCH_SIZE + 1}: {r.status_code} {r.text[:200]}")
        except Exception as e:
            err += len(batch)
            print(f"  Exception: {str(e)}")
        time.sleep(3)
        
    print(f"\nDEEP SEO FINISHED: {ok} OK, {err} ERR")

if __name__ == "__main__":
    apply_deep_seo()
