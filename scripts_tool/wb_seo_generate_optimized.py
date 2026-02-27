# -*- coding: utf-8 -*-
"""
ГЕНЕРАТОР SEO-ОПТИМИЗИРОВАННЫХ КАРТОЧЕК
На основе аудита создает улучшенные версии
"""
import json
import os
from typing import Dict, Any

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
AUDIT_PATH = os.path.join(BASE_DIR, 'WB_SEO_AUDIT_REPORT.json')
OPTIMIZED_PATH = os.path.join(BASE_DIR, 'WB_SEO_OPTIMIZED_CARDS.json')

# Загрузка данных
with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open(AUDIT_PATH, 'r', encoding='utf-8') as f:
    audit = json.load(f)

# Создаем словарь карточек по NM_ID
cards_dict = {c['nmID']: c for c in cards}

# Получаем худшие карточки (балл < 60)
poor_cards = [s for s in audit['seo_scores'] if s['score'] < 60]

print(f"╔══════════════════════════════════════════════════════════════╗")
print(f"║  ГЕНЕРАТОР SEO-ОПТИМИЗИРОВАННЫХ КАРТОЧЕК                     ║")
print(f"║  Карточек для оптимизации: {len(poor_cards):3d}                            ║")
print(f"╚══════════════════════════════════════════════════════════════╝\n")

# SEO шаблоны
CATEGORY_TEMPLATES = {
    'именной': {
        'title_prefix': 'Именной браслет с гравировкой',
        'keywords': ['персональная гравировка', 'именной подарок', '2026', 'сталь 316L'],
        'usp': [
            'Персональная лазерная гравировка имени или даты',
            'Нержавеющая медицинская сталь 316L - не темнеет, гипоаллергенно',
            'Регулируемый размер - подходит на любую руку',
            'Подарочная упаковка в комплекте'
        ]
    },
    'зодиак': {
        'title_prefix': 'Браслет Зодиак гравировка',
        'keywords': ['знак зодиака', 'астрология', 'именной', '2026'],
        'usp': [
            'Символ знака зодиака с персональной гравировкой',
            'Стильный минималистичный дизайн',
            'Нержавеющая сталь - долговечность гарантирована',
            'Идеальный подарок для ценителей астрологии'
        ]
    },
    'армия': {
        'title_prefix': 'Армейский браслет с гравировкой',
        'keywords': ['военнослужащему', 'армия', 'служба', '2026'],
        'usp': [
            'Для военнослужащих - гравировка звания, части, даты',
            'Прочная конструкция из стали 316L',
            'Сдержанный мужской дизайн',
            'Символ службы и патриотизма'
        ]
    },
    'семья': {
        'title_prefix': 'Семейный браслет гравировка',
        'keywords': ['для семьи', 'родственникам', 'близким', '2026'],
        'usp': [
            'Гравировка имен всей семьи или важных дат',
            'Символ единства и любви',
            'Качественное исполнение - передается поколениям',
            'Универсальный подарок для родных'
        ]
    },
    'default': {
        'title_prefix': 'Браслет с гравировкой',
        'keywords': ['персональный', 'подарок', 'именной', '2026'],
        'usp': [
            'Индивидуальная лазерная гравировка',
            'Медицинская нержавеющая сталь 316L',
            'Современный стильный дизайн',
            'Подарочная упаковка включена'
        ]
    }
}

def detect_category(card: Dict[str, Any]) -> str:
    """Определяет категорию карточки"""
    title = card.get('title', '').lower()
    vc = card.get('vendorCode', '').lower()
    combined = title + ' ' + vc
    
    if 'именной' in combined or 'имя' in combined:
        return 'именной'
    elif 'зодиак' in combined or 'астро' in combined:
        return 'зодиак'
    elif 'армия' in combined or 'военн' in combined:
        return 'армия'
    elif 'семья' in combined or 'семей' in combined:
        return 'семья'
    return 'default'

def generate_optimized_title(card: Dict[str, Any], category: str) -> str:
    """Генерирует оптимизированный заголовок"""
    template = CATEGORY_TEMPLATES[category]
    prefix = template['title_prefix']
    
    # Добавляем специфику если есть
    old_title = card.get('title', '')
    
    # Извлекаем уникальные детали из старого заголовка
    details = ''
    if 'мужской' in old_title.lower():
        details = 'мужской'
    elif 'женский' in old_title.lower():
        details = 'женский'
    
    # Формируем новый заголовок
    if details:
        new_title = f"{prefix} {details} подарок 2026"
    else:
        new_title = f"{prefix} подарок 2026"
    
    # Обрезаем до 60 символов
    if len(new_title) > 60:
        new_title = new_title[:57] + "..."
    
    return new_title

def generate_optimized_description(card: Dict[str, Any], category: str) -> str:
    """Генерирует оптимизированное описание"""
    template = CATEGORY_TEMPLATES[category]
    
    # Вступление
    intro = f"Эксклюзивный {template['title_prefix'].lower()} от бренда GRAVMIX - это персональный подарок, который несет особый смысл и подчеркивает индивидуальность."
    
    # УТП
    usp_section = "\n\n✨ ПРЕИМУЩЕСТВА:\n" + "\n".join([f"• {usp}" for usp in template['usp']])
    
    # Применение
    application = "\n\n🎁 ИДЕАЛЬНЫЙ ПОДАРОК:\n• На день рождения, 23 февраля, Новый год 2026\n• Для близкого человека, друга, коллеги\n• На годовщину, свадьбу, выпускной\n• Просто чтобы порадовать"
    
    # Качество
    quality = "\n\n⚡ КАЧЕСТВО И ГАРАНТИИ:\n• Изделия от производителя GRAVMIX\n• Гравировка выполняется профессиональным лазерным оборудованием\n• Материалы высшего качества - сталь 316L (медицинская)\n• Не темнеет, не вызывает аллергии, служит годами"
    
    # Призыв к действию
    cta = "\n\n📦 ОФОРМИТЕ ЗАКАЗ СЕЙЧАС!\nБыстрая доставка по всей России. Подарочная упаковка в комплекте. Персональная гравировка в течение 1-2 дней."
    
    # Ключевые слова для SEO
    keywords = f"\n\nКлючевые слова: {', '.join(template['keywords'])}"
    
    full_desc = intro + usp_section + application + quality + cta + keywords
    
    # Обрезаем если слишком длинное
    if len(full_desc) > 5000:
        full_desc = full_desc[:4990] + "\n..."
    
    return full_desc

# Генерируем оптимизированные карточки
optimized_cards = []

for score_data in poor_cards:
    nm_id = score_data['nm_id']
    card = cards_dict.get(nm_id)
    
    if not card:
        continue
    
    category = detect_category(card)
    
    optimized = {
        'nm_id': nm_id,
        'vendor_code': card.get('vendorCode'),
        'category': category,
        'old_score': score_data['score'],
        'issues': score_data['issues'],
        'old_title': card.get('title'),
        'new_title': generate_optimized_title(card, category),
        'old_description': card.get('description'),
        'new_description': generate_optimized_description(card, category),
        'recommendations': []
    }
    
    # Добавляем рекомендации
    if len(card.get('photos', [])) < 4:
        optimized['recommendations'].append(f"Добавить фото: сейчас {len(card.get('photos', []))}, нужно минимум 4-8")
    
    if len(card.get('characteristics', [])) < 5:
        optimized['recommendations'].append(f"Добавить характеристики: сейчас {len(card.get('characteristics', []))}, нужно минимум 5")
    
    optimized_cards.append(optimized)

# Сохраняем результат
output = {
    'total_optimized': len(optimized_cards),
    'categories': {},
    'cards': optimized_cards
}

# Группируем по категориям
for card in optimized_cards:
    cat = card['category']
    if cat not in output['categories']:
        output['categories'][cat] = 0
    output['categories'][cat] += 1

with open(OPTIMIZED_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✓ Создано оптимизированных карточек: {len(optimized_cards)}")
print(f"\nРаспределение по категориям:")
for cat, count in output['categories'].items():
    print(f"  {cat}: {count} карточек")

print(f"\n✓ Результат сохранен: {OPTIMIZED_PATH}")
print(f"\nПример оптимизации первой карточки:")
print("─" * 60)
first = optimized_cards[0]
print(f"NM_ID: {first['nm_id']}")
print(f"Категория: {first['category']}")
print(f"Старый балл: {first['old_score']}/100")
print(f"\nСтарый заголовок ({len(first['old_title'])} символов):")
print(f"  {first['old_title']}")
print(f"\nНовый заголовок ({len(first['new_title'])} символов):")
print(f"  {first['new_title']}")
print(f"\nРекомендации:")
for rec in first['recommendations']:
    print(f"  • {rec}")
