# -*- coding: utf-8 -*-
"""
WB Unit Economics and Final Ad Audit computation
"""
import os, json

# 1. Base inputs from WB
ORDERS_30D = 380
SALES_30D = 372
REVENUE_30D = 238701
PAYOUT_30D = 243491

# Constants (Cost per item)
COST = 110
PACKAGING = 15
TOTAL_COGS_PER_UNIT = COST + PACKAGING

# Averages
AVG_TICKET_WB = REVENUE_30D / SALES_30D if SALES_30D else 0
AVG_PAYOUT_WB = PAYOUT_30D / SALES_30D if SALES_30D else 0

# Note on WB pricing logic:
# Revenue (priceWithDisc) is usually what the buyer pays before WB's SPP discount.
# Payout is what seller receives (Base Price - Discount - SPP + SPP_Compensation - WB_Commission - Logistics)
# If PAYOUT > REVENUE, it means SPP compensation from WB exceeds their commission + logistics.
# This happens often on WB when they aggressively subsidize sales.

print("=====================================================================")
print("ЮНИТ-ЭКОНОМИКА WILDBERRIES (На основе API данных за 30 дней)")
print("=====================================================================")

print(f"\nБАЗОВЫЕ ПОКАЗАТЕЛИ (30 дней):")
print(f"  Заказов:            {ORDERS_30D}")
print(f"  Выкупов:            {SALES_30D} (процент выкупа {(SALES_30D/ORDERS_30D)*100:.1f}%)")
print(f"  Оборот (оплачено):  {REVENUE_30D:,.0f} ₽")
print(f"  К выплате:          {PAYOUT_30D:,.0f} ₽")

print(f"\nНА 1 ТОВАР В СРЕДНЕМ:")
print(f"  Цена покупки:        {AVG_TICKET_WB:,.0f} ₽")
print(f"  Выплата селлеру:     {AVG_PAYOUT_WB:,.0f} ₽")
print(f"  Себестоимость:      -{TOTAL_COGS_PER_UNIT:,.0f} ₽")
profit_before_tax = AVG_PAYOUT_WB - TOTAL_COGS_PER_UNIT
print(f"  Прибыль до налогов:  {profit_before_tax:,.0f} ₽")

# TAXES
# On WB, for USN 6% "Доходы", the tax base is the FULL price the buyer pays (finishedPrice) + SPP compensation.
# Usually, the tax base on WB is the 'retail_price' (what buyer pays) + 'spp' (what WB pays for buyer).
# Essentially, tax base ≈ REVENUE_30D (or slightly more depending on report details).
tax_per_unit = AVG_TICKET_WB * 0.06
net_profit_unit = profit_before_tax - tax_per_unit

print(f"\nС УЧЕТОМ НАЛОГА (УСН 6%):")
print(f"  Налог 6% (от {AVG_TICKET_WB:.0f}₽): -{tax_per_unit:.1f} ₽")
print(f"  Чистая прибыль:      {net_profit_unit:.1f} ₽")
print(f"  Маржинальность:      {(net_profit_unit/AVG_TICKET_WB)*100:.1f}%")

print(f"\nМЕСЯЧНАЯ ЭКОНОМИКА WB:")
monthly_cogs = SALES_30D * TOTAL_COGS_PER_UNIT
monthly_tax = REVENUE_30D * 0.06
monthly_profit = PAYOUT_30D - monthly_cogs - monthly_tax
print(f"  Выплата:             {PAYOUT_30D:,.0f} ₽")
print(f"  - Себестоимость:    -{monthly_cogs:,.0f} ₽")
print(f"  - Налог 6%:         -{monthly_tax:,.0f} ₽")
print(f"  ---------------------------------")
print(f"  ЧИСТАЯ ПРИБЫЛЬ:      {monthly_profit:,.0f} ₽/мес")

# Ad Budget limits
print(f"\nБЮДЖЕТ НА РЕКЛАМУ WB:")
print(f"  Чтобы рекл. продажа не уходила в минус (Break-even CPO): {net_profit_unit:.0f} ₽/заказ")
safe_cpo = net_profit_unit * 0.5
print(f"  Безопасный CPO (50% прибыли): {safe_cpo:.0f} ₽/заказ")
print(f"  Если хотим X заказов с рекламы, бюджет должен быть: X * {safe_cpo:.0f} ₽")

# Compare with Ozon
print("\nСРАВНЕНИЕ: WB vs OZON (на единицу продукта):")
print(f"  Метрика          | WB          | Ozon")
print(f"  -----------------|-------------|-------------")
print(f"  Средний чек      | {AVG_TICKET_WB:>8.0f} ₽  |  1,428 ₽")
print(f"  Выплата (payout) | {AVG_PAYOUT_WB:>8.0f} ₽  |    618 ₽")
print(f"  Чистая прибыль   | {net_profit_unit:>8.0f} ₽  |    392 ₽")
print(f"  Маржа            | {(net_profit_unit/AVG_TICKET_WB)*100:>7.1f}%  |   27.5%")
