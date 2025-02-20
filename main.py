import json
import re
import os
import requests
from pprint import pprint

from objects.store import Store


class CouponStatus:
    AVAILABLE = 'Available'
    REDEEMED = 'Redeemed'
    ACTIVATED = 'Activated'
    EXPIRED = 'ExpiredClipped'


def load_store_info():
    with open('.store_settings', 'r') as file:
        data = json.load(file)
    stores = []
    for store in data:
        stores.append(login(store))
    return stores


def extract_store_id_and_token(url):
    res = requests.get(url)
    with open('app.js', 'w') as f:
        f.write(res.text)
    marker = '"https://webservices.brdata.com/api"'  # Exact marker

    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()  # Read the entire file as a single string

    match = re.search(re.escape(marker) + r'.*?"([^"]+)"\s*.*?"([^"]+)"', content)
    os.remove('app.js')

    if match:
        return match.group(1), match.group(2)  # Extract and return both values
    return None, None  # No match found


def login(store_json):
    name = store_json['StoreName']
    app_url = store_json['app.js']
    store_id, login_token = extract_store_id_and_token(store_json['app.js'])
    return Store(name=name, store_id=store_id, login_token=login_token)


if __name__ == '__main__':
    stores = load_store_info()

    for store in stores:
        coupons = store.get_available_coupons()
        store.get_coupon_summary()