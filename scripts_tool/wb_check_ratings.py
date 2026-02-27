# -*- coding: utf-8 -*-
"""
ПРОВЕРКА РЕЙТИНГОВ ТОВАРОВ WILDBERRIES
Поиск товаров с низким рейтингом (<4.0) для клонирования
"""
import json
import os

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')

print("╔══════════════════════════════════════════════════════════════╗")
print("║  ПРОВЕРКА РЕЙТИНГОВ ТОВАРОВ - СТРАТЕГИЯ КЛОНИРОВАНИЯ         ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Загрузка карточек
with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f"📋 Всего опубликованных карточек: {len(cards)}\n")

# В WB API v2 нет прямого рейтинга в карточке
# Но мы можем проверить через Statistics API или вручную

# На основе скриншотов видим товары с рейтингом
# Например: 4.3, 5.0, 4.5, 4.0, 4.5, 5.0

# Для демонстрации создадим список на основе видимых данных
print("🔍 АНАЛИЗ КАРТОЧЕК НА СКРИНШОТЕ:")
print("─" * 70)

# Видимые на скриншоте
screenshot_ratings = [
    {'nm_id': 296461510, 'rating': 4.3, 'title': 'Браслет с гравировкой имен'},
    {'nm_id': 296448013, 'rating': 5.0, 'title': 'Браслет с гравировкой имен подарок'},
    {'nm_id': 296462523, 'rating': 4.5, 'title': 'Браслет с гравировкой имен'},
    {'nm_id': 279467514, 'rating': 5.0, 'title': 'Браслет с гравировкой для любимого'},
    {'nm_id': 217918877, 'rating': 4.5, 'title': 'Браслет с гравировкой Я люблю тебя'},
    {'nm_id': 216301049, 'rating': 4.0, 'title': 'Браслет с гравировкой Ты мое счастье'},
    {'nm_id': 199699063, 'rating': 5.0, 'title': 'Браслет с гравировкой Я тебя'},
    {'nm_id': 198595027, 'rating': None, 'title': 'Браслет с гравировкой Птицы'},
    {'nm_id': 198595031, 'rating': None, 'title': 'Браслет с гравировкой Слово Пацана'}
]

low_ratings = [r for r in screenshot_ratings if r['rating'] and r['rating'] < 4.5]
no_ratings = [r for r in screenshot_ratings if not r['rating']]

print(f"Товары с рейтингом < 4.5 (требуют клонирования):")
for r in low_ratings:
    print(f"  🔴 NM_{r['nm_id']}: рейтинг {r['rating']} - {r['title'][:50]}")

print(f"\nТовары без рейтинга (новые или нет отзывов):")
for r in no_ratings:
    print(f"  ⚪ NM_{r['nm_id']}: нет рейтинга - {r['title'][:50]}")

# Проверка всех карточек
print(f"\n📊 АВТОМАТИЧЕСКАЯ ПРОВЕРКА ВСЕХ КАРТОЧЕК:")
print("─" * 70)

# Для каждой карточки проверяем заголовок на признаки проблем
problem_keywords = ['ошибка', 'брак', 'возврат', 'плохо']
potential_problems = []

for card in cards:
    title = card.get('title', '').lower()
    desc = card.get('description', '').lower()
    nm_id = card.get('nmID')
    
    # Простая эвристика - если в описании упоминаются проблемы
    if any(kw in title + desc for kw in problem_keywords):
        potential_problems.append({
            'nm_id': nm_id,
            'title': card.get('title'),
            'vendor_code': card.get('vendorCode')
        })

if potential_problems:
    print(f"⚠️ Найдено {len(potential_problems)} карточек с потенциальными проблемами")
    for p in potential_problems[:5]:
        print(f"  • NM_{p['nm_id']}: {p['title'][:50]}")
else:
    print("✓ Автоматически проблем не обнаружено")

# Рекомендации по клонированию
print(f"\n🎯 РЕКОМЕНДАЦИИ ПО КЛОНИРОВАНИЮ:")
print("─" * 70)

clone_candidates = []

# На основе известных данных
if low_ratings:
    print(f"\n1. КРИТИЧНО - Клонировать {len(low_ratings)} товаров с низким рейтингом:")
    for r in low_ratings:
        nm_id = r['nm_id']
        # Находим полную карточку
        full_card = next((c for c in cards if c.get('nmID') == nm_id), None)
        if full_card:
            clone_candidates.append({
                'nm_id': nm_id,
                'vendor_code': full_card.get('vendorCode'),
                'title': full_card.get('title'),
                'rating': r['rating'],
                'reason': f"Низкий рейтинг {r['rating']}"
            })
            print(f"   • NM_{nm_id} (рейтинг {r['rating']})")
            print(f"     VC: {full_card.get('vendorCode')}")
            print(f"     Новый VC: {full_card.get('vendorCode')}_CLONED")

# Сохранение списка для клонирования
output = {
    'generated_at': '2026-02-27',
    'total_candidates': len(clone_candidates),
    'strategy': 'Re-creation: клонирование с новыми штрихкодами для обнуления рейтинга',
    'candidates': clone_candidates,
    'next_steps': [
        '1. Создать скрипт Perfect Clone для копирования карточек',
        '2. Новый vendorCode = старый + "_CLONED"',
        '3. Скопировать все: фото, описание, характеристики, габариты',
        '4. Пустой массив skus для автогенерации штрихкодов',
        '5. После создания - запустить самовыкупы для первых отзывов'
    ]
}

output_path = os.path.join(ANALYTICS_DIR, 'wb_clone_candidates.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✓ Список кандидатов на клонирование сохранен:")
print(f"  {output_path}")

print(f"\n📝 СЛЕДУЮЩИЕ ШАГИ:")
print("  1. Создать скрипт wb_perfect_clone.py")
print("  2. Протестировать на 1 карточке")
print("  3. Клонировать все проблемные позиции")
print("  4. Запустить стратегию продвижения новых карточек")
print()
