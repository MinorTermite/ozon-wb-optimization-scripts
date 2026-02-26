---
description: Экстренное восстановление цен на Wildberries
---
Этот ворклоу восстанавливает цены на WB до базового уровня (1548₽) для всех 266 товаров.

1. Убедитесь, что в файле `.env` указан верный API-ключ Wildberries.
2. Запустите скрипт восстановления:
// turbo
```powershell
python scripts_tool/wb_restore_prices.py
```
3. После завершения проверьте статус в личном кабинете WB или запустите аудит цен:
// turbo
```powershell
python scripts_tool/wb_price_audit.py
```
