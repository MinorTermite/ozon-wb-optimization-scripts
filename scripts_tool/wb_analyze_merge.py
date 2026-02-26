import json
import collections
import re

def clean_title(title):
    t = title.lower()
    t = t.replace('gravmix', '').replace('из стали 316l', '').replace('из нержавеющей стали', '').replace('с гравировкой', '')
    t = t.replace('подарок', '').replace('браслет', '').replace('брелок для ключей', '').replace('брелок', '').replace('жетон', '')
    # remove extra spaces
    return " ".join(t.split())

def analyze_merging():
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    # 1. SEO Stats
    short_titles = 0
    short_desc = 0
    
    # 2. Grouping
    zodiac_signs = ['овен', 'телец', 'близнец', 'рак', 'лев', 'дев', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыб']
    
    groups = collections.defaultdict(list)
    
    for c in cards:
        title = c.get('title', '')
        desc = c.get('description', '')
        vc = c.get('vendorCode', '')
        nm = c.get('nmID', '')
        
        if len(title) < 20: short_titles += 1
        if len(desc) < 500: short_desc += 1
        
        t_low = title.lower()
        
        # Determine group
        group_name = "Uncategorized"
        
        if any(z in t_low for z in zodiac_signs) and 'браслет' in t_low:
            group_name = "Браслеты: Знаки Зодиака"
        elif 'муж' in t_low or 'пап' in t_low or 'сын' in t_low or 'дедуш' in t_low or 'брат' in t_low:
            if 'браслет' in t_low: group_name = "Браслеты: Мужские / Семья"
            elif 'брелок' in t_low or 'жетон' in t_low: group_name = "Брелоки: Мужские / Семья"
        elif 'жен' in t_low or 'мам' in t_low or 'доч' in t_low or 'бабуш' in t_low or 'сестр' in t_low:
            if 'браслет' in t_low: group_name = "Браслеты: Женские / Семья"
            elif 'брелок' in t_low: group_name = "Брелоки: Женские / Семья"
        elif 'парн' in t_low or 'влюбл' in t_low or 'половинк' in t_low:
            group_name = "Парные украшения"
        elif 'авто' in t_low or 'машин' in t_low or 'номер' in t_low:
            group_name = "Брелоки: Автомобильные"
        else:
            # Fallback to base category
            cleaned = clean_title(title)
            if 'браслет' in t_low: group_name = f"Браслеты: Разное ({cleaned[:15]})"
            elif 'брелок' in t_low: group_name = f"Брелоки: Разное ({cleaned[:15]})"
            elif 'подвеск' in t_low or 'кулон' in t_low: group_name = "Подвески"
            
        groups[group_name].append({'title': title, 'vc': vc, 'nm': nm})
        
    print(f"=== SEO AUDIT SUMMARY ===")
    print(f"Total cards: {len(cards)}")
    print(f"Cards with short titles (<20 chars): {short_titles}")
    print(f"Cards with short descriptions (<500 chars): {short_desc}")
    print(f"\n=== MERGE GROUPINGS (Предложения по склейке) ===")
    
    for gname, items in sorted(groups.items(), key=lambda x: -len(x[1])):
        print(f"\nГруппа: {gname} (Кол-во: {len(items)})")
        if len(items) > 1:
            print("  -> Эту группу можно склеить в одну карточку с разными вариантами.")
            for item in items[:5]:
                print(f"     - {item['title']} [{item['vc']}]")
            if len(items) > 5:
                print(f"     ... и еще {len(items)-5} товаров")
        else:
            print("  -> Слишком мало товаров для целевой склейки.")

if __name__ == "__main__":
    analyze_merging()
