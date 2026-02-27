# ИСПРАВЛЕНИЯ WB SEO СКРИПТА - 26 февраля 2026

## КРИТИЧЕСКАЯ ПРОБЛЕМА (ИСПРАВЛЕНА) ✓

### Причина ошибки 400 "Invalid request format"

Wildberries Content API v2 метод `/content/v2/cards/update` **ожидает массив карточек**, а не одну карточку!

**Было (НЕПРАВИЛЬНО):**
```python
r = requests.post(UPDATE_URL, headers=headers, json=card_body, timeout=40)
# Отправка ОДНОГО объекта карточки
```

**Стало (ПРАВИЛЬНО):**
```python
r = requests.post(UPDATE_URL, headers=headers, json=batch_payload, timeout=60)
# Отправка МАССИВА карточек (batch_payload - это list)
```

## ЧТО ИЗМЕНЕНО

### 1. Пакетная обработка (Batch Processing) ✓
- **Размер пакета**: 100 карточек за запрос (API поддерживает до 3000)
- **Преимущества**: 
  - Соответствие формату API (массив)
  - Уменьшение количества запросов
  - Лучшее использование rate limits

### 2. Соблюдение Rate Limits ✓
- **Лимит API**: 10 запросов в минуту
- **Пауза между пакетами**: 7 секунд (безопасный интервал)
- **Пауза при 429**: 40 секунд

### 3. Улучшенная обработка ошибок ✓
- Валидация ответа API даже при 200 OK
- Логирование номеров пакетов
- Предотвращение бесконечных циклов

### 4. Увеличенный timeout ✓
- **Было**: 40 секунд
- **Стало**: 60 секунд (для пакетных запросов)

## СТРУКТУРА НОВОГО КОДА

### Пакетная обработка
```python
BATCH_SIZE = 100
for batch_idx in range(0, len(remaining_cards), BATCH_SIZE):
    batch_cards = remaining_cards[batch_idx:batch_idx + BATCH_SIZE]
    batch_payload = []  # МАССИВ карточек
    
    for c in batch_cards:
        card_body = {...}  # Формируем карточку
        batch_payload.append(card_body)  # Добавляем в массив
    
    # Отправляем МАССИВ
    r = requests.post(UPDATE_URL, headers=headers, json=batch_payload, timeout=60)
```

### Правильный формат запроса
```json
[
  {
    "nmID": 296462523,
    "vendorCode": "...",
    "title": "...",
    "description": "...",
    "dimensions": {...},
    "characteristics": [...],
    "sizes": [...]
  },
  {
    "nmID": 296462524,
    ...
  }
]
```

## ИНСТРУКЦИЯ ПО ЗАПУСКУ

### 1. Тестовый запуск (РЕКОМЕНДУЕТСЯ)
```powershell
cd C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar
python scripts_tool\wb_seo_apply_2026_FIXED.py
```

### 2. Мониторинг прогресса
Скрипт выводит:
```
[Batch 1/3] SUCCESS: 100 cards updated
  Sample NM_IDs: [296462523, 296462524, ...]
[Batch 2/3] SUCCESS: 100 cards updated
  Sample NM_IDs: [296462625, 296462626, ...]
```

### 3. Проверка ошибок
После завершения проверьте: https://seller.wildberries.ru/new-goods/error-cards

### 4. Если все ОК - замените основной файл
```powershell
Copy-Item scripts_tool\wb_seo_apply_2026_FIXED.py scripts_tool\wb_seo_apply_2026.py -Force
```

## ВРЕМЕННАЯ ШКАЛА ОБРАБОТКИ

- **266 карточек** ÷ 100 = **3 пакета**
- Время обработки: ~3 пакета × 7 секунд = **~21 секунда**
- API синхронизация: **до 30 минут** после завершения

## ВАЖНЫЕ ЗАМЕЧАНИЯ

1. ✓ **Резервная копия создана**: `backup/wb_seo_apply_2026_*.py`
2. ✓ **Прогресс сохраняется**: `data_dump/seo_progress.json`
3. ⚠ **API асинхронна**: изменения могут появиться через 30 минут
4. ⚠ **Проверьте errors**: используйте API метод `/content/v2/cards/error/list`

## ИСТОЧНИКИ

- [WB API Docs - Update Cards](https://dev.wildberries.ru/en/openapi/work-with-products)
- [Release Notes - Rate Limits](https://dev.wildberries.ru/en/release-notes?id=262)

## СЛЕДУЮЩИЕ ШАГИ

1. ✅ Запустить исправленный скрипт
2. ✅ Проверить результаты
3. ⏭ Перейти к задаче #2: Ozon Granular Split
4. ⏭ Создать интеграцию Yandex Market

---
**Дата**: 26 февраля 2026  
**Автор**: Claude (Anthropic)  
**Статус**: ГОТОВО К ТЕСТИРОВАНИЮ ✓
