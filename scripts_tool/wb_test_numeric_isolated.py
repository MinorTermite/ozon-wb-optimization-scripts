import requests
import json
import time

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def check_error(vc):
    url = "https://content-api.wildberries.ru/content/v2/cards/error/list"
    r = requests.post(url, headers=H, json={"locale": "ru"})
    if r.status_code == 200:
        data = r.json().get('data', [])
        # Properly handle the nested dict structure of error list
        # data is a list of batches
        if isinstance(data, dict): # Sometimes it's a dict containing 'items'
            data = data.get('items', [])
            
        for batch in data:
            subjects = batch.get('subjects', {})
            for subj_name, subj_data in subjects.items():
                errors_dict = subj_data.get('errors', {})
                if vc in errors_dict:
                    return errors_dict[vc]
    return None

def test_isolated(vc, nmID, char_id, char_name, char_val, label):
    print(f"\n TESTING: {label} ({repr(char_val)})")
    
    # We must send a full card to be sure
    body = [{
        "nmID": nmID,
        "vendorCode": vc,
        "characteristics": [
            {
                "id": char_id,
                "name": char_name,
                "value": char_val
            }
        ],
        "dimensions": {
            "width": 5,
            "height": 2,
            "length": 5,
            "weightBrutto": 0.05
        }
    }]
    
    r = requests.post("https://content-api.wildberries.ru/content/v2/cards/update", headers=H, json=body)
    print(f"  API Response Status: {r.status_code}")
    
    print("  Waiting 10 seconds for WB processing...")
    time.sleep(10)
    
    errs = check_error(vc)
    if errs:
        print(f"  Result: FAILED. WB says: {errs}")
        return False
    else:
        print("  Result: PASSED (or no errors yet)!")
        return True

if __name__ == "__main__":
    nmID = 204248729
    vc = "wb5i9ylyy48"
    char_id = 90673
    char_name = "Ширина предмета"

    # We will only test the two most likely candidates
    # 1. List of Strings (Standard)
    # 2. Single Int (What was in the dump)
    
    test_isolated(vc, nmID, char_id, char_name, ["5"], "List of Strings")
    test_isolated(vc, nmID, char_id, char_name, 5, "Single Int")
