import json
import os

DUMP_PATH = 'scripts_tool/wb_cards_seo_dump.json'
if not os.path.exists(DUMP_PATH):
    DUMP_PATH = 'wb_cards_seo_dump.json'

if not os.path.exists(DUMP_PATH):
    print(f"Error: {DUMP_PATH} not found.")
    exit(1)

with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f"Auditing {len(cards)} cards for WB validation errors...")

too_long = []
bad_brand = []
no_brand = []

for c in cards:
    nm_id = c.get('nmID')
    title = str(c.get('title', ''))
    brand = str(c.get('brand', ''))
    
    # 60 char limit check
    if len(title) > 60:
        too_long.append({
            'nmID': nm_id,
            'title': title,
            'len': len(title)
        })
        
    # Brand check: User said GRAVMIX brand does not exist yet on WB
    if brand == 'GRAVMIX':
        bad_brand.append({
            'nmID': nm_id,
            'vendorCode': c.get('vendorCode')
        })
    elif not brand:
        no_brand.append(nm_id)

print(f"\nRESULTS:")
print(f" - Too long titles (>60): {len(too_long)}")
# Use list comprehension instead of slice to satisfy IDE linter
too_long_list = list(too_long)
for i in range(min(5, len(too_long_list))):
    item = too_long_list[i]
    print(f"   [{item['nmID']}] ({item['len']} chars): {item['title']}")
if len(too_long_list) > 5: print("   ...")

print(f"\n - Forbidden brand 'GRAVMIX': {len(bad_brand)}")
bad_brand_list = list(bad_brand)
for i in range(min(5, len(bad_brand_list))):
    item = bad_brand_list[i]
    print(f"   [{item['nmID']}] VC: {item['vendorCode']}")

print(f"\n - Missing brand: {len(no_brand)}")

# Ensure data_dump exists
os.makedirs('data_dump', exist_ok=True)
with open('data_dump/wb_seo_errors_found.json', 'w', encoding='utf-8') as f:
    json.dump({'too_long': too_long, 'bad_brand': bad_brand}, f, indent=2)
