import json, re, os, requests, sys
from logger import Logger as StoreLogger

from objects.store import Store

_logger = StoreLogger()


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
        _logger.log(f'Successfully extracted token from {url}')
        return match.group(1), match.group(2)  # Extract and return both values
    return None, None  # No match found


def login(store_json):
    name = store_json['StoreName']
    app_url = store_json['app.js']
    store_id, login_token = extract_store_id_and_token(app_url)
    return Store(name=name, store_id=store_id, login_token=login_token)


def start_dialog():
    stores = load_store_info()

    while (True):
        i = input('Action (clipCoupons / summarize): ')
        if i.__contains__('clip'):
            for store in stores:
                store.clip(store.get_available_coupons())
        elif i == 'summarize':
            for store in stores:
                store.try_get_all_coupons()
        elif i == 'details':
            for store in stores:
                for coupon in store.get_available_coupons():
                    print(f'Brand: {coupon.brand_name}')
                    print(f'Description: {coupon.offer_description}')
                    print(f'Value: {coupon.offer_value}')
        elif i == 'reload':
            stores = load_store_info()
        elif i == 'exit':
            exit()
        else:
            print('Invalid.')


def start_automated():
    for store in load_store_info():
        store.clip(store.get_available_coupons())


if __name__ == '__main__':
    if len(sys.argv) == 1:
        _logger.log('Started program in dialog mode')
        start_dialog()
    else:
        _logger.log('Started program in automated mode')
        start_automated()
