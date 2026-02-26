"""
Test all possible auth formats for Yandex Market Partner API.
"""
import requests

API_KEY = "ACMA:lkqaJ3BufmaoB9DEyxLPFtGHmbpy4AP7LnqK4eSh:03511baf"
BUSINESS_ID = 216491430

BASE_URL = "https://api.partner.market.yandex.ru"

# Test multiple authorization header formats
auth_formats = [
    ("Api-Key header (full)", {"Api-Key": API_KEY, "Content-Type": "application/json"}),
    ("Authorization Api-Key", {"Authorization": f"Api-Key {API_KEY}", "Content-Type": "application/json"}),
    ("Authorization Bearer", {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}),
    ("OAuth header", {"Authorization": f"OAuth {API_KEY}", "Content-Type": "application/json"}),
]

# Test endpoints
endpoints = [
    ("POST offer-cards", "POST", f"{BASE_URL}/businesses/{BUSINESS_ID}/offer-cards", {"limit": 1}),
    ("GET campaigns", "GET", f"{BASE_URL}/campaigns", None),
    ("GET businesses", "GET", f"{BASE_URL}/businesses/{BUSINESS_ID}", None),
]

print("=== ТЕСТ АВТОРИЗАЦИИ YANDEX MARKET API ===\n")

for auth_name, auth_headers in auth_formats:
    print(f"\n[{auth_name}]")
    for ep_name, method, url, body in endpoints[:2]:
        try:
            if method == "POST":
                res = requests.post(url, headers=auth_headers, json=body, timeout=10)
            else:
                res = requests.get(url, headers=auth_headers, timeout=10)
            
            if res.status_code in (200, 201):
                print(f"  ✅ {ep_name}: {res.status_code} — РАБОТАЕТ!")
                print(f"     {str(res.text[:200])}")
            else:
                print(f"  ❌ {ep_name}: {res.status_code} — {res.text[:150]}")
        except Exception as e:
            print(f"  ❌ {ep_name}: Exception — {e}")
