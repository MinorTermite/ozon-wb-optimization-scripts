import requests
import json
import datetime

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))
H = {'Authorization': env['WB_API_KEY']}

def audit_wb_prices():
    print("Fetching orders for the last 14 days...")
    date_from = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')
    r = requests.get(f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_from}', headers=H)
    
    if r.status_code != 200:
        print(f"Error: {r.status_code} {r.text}")
        return

    orders = r.json()
    print(f"Total orders found: {len(orders)}")
    
    # Sort orders by date
    orders.sort(key=lambda x: x['date'], reverse=True)
    
    print("\nRecent Orders Analysis:")
    print(f"{'Date':<20} | {'nmId':<12} | {'PriceWithDisc':<12} | {'TotalPrice':<12} | {'FinishedPrice':<12}")
    print("-" * 75)
    
    for o in orders[:50]:
        date = o.get('date', '')
        nmid = o.get('nmId', '')
        pwd = o.get('priceWithDisc', 0)
        total = o.get('totalPrice', 0)
        finished = o.get('finishedPrice', 0) # What buyer actually paid after all discounts
        print(f"{date:<20} | {nmid:<12} | {pwd:<12} | {total:<12} | {finished:<12}")

    # Check for price changes
    # Calculate daily average finishedPrice
    daily_stats = {}
    for o in orders:
        day = o['date'][:10]
        if day not in daily_stats: daily_stats[day] = []
        daily_stats[day].append(o.get('finishedPrice', 0))
    
    print("\nDaily Average Finished Price (Buyer Price):")
    for day in sorted(daily_stats.keys()):
        prices = daily_stats[day]
        avg = sum(prices) / len(prices)
        print(f"  {day}: {avg:.2f} ₽ ({len(prices)} orders)")

if __name__ == "__main__":
    audit_wb_prices()
