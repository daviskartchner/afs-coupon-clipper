import json
import re
import os
import requests
from pprint import pprint

class CouponStatus:
    AVAILABLE = 'Available'
    REDEEMED = 'Redeemed'
    ACTIVATED = 'Activated'
    EXPIRED = 'ExpiredClipped'

def _generate_payload(coupons):
    if type(coupons) == type(list()):
        offer_ids = []
        for coupon in coupons:
            offer_ids.append(coupon.offer_id)
    else:
        offer_ids = coupons.offer_id
    return {'offers': offer_ids}

def get_login_credentials():
    with open('.login_settings', 'r') as file:
        return json.load(file)

class Store:
    def __init__(self, name, store_id, login_token):
        self.name = name
        self.store_id = store_id
        self.headers = None

        self.loyalty_id = self.login(login_token)
        self.base_url = f'https://webservices.brdata.com/api/loyalty/{self.store_id}/quotient/{self.loyalty_id}/offers'

        self.coupons = None
        self.available_coupons = None
        self.activated_coupons = None
        self.expiredclipped_coupons = None
        self.redeemed_coupons = None


    def login(self, login_token):
        self.headers = {'Authorization': f'Bearer {login_token}'}
        login_url = f'https://webservices.brdata.com/api/AppUsers/login?a={self.store_id}'
        body = get_login_credentials()
        res = requests.post(login_url, headers=self.headers, json=body)
        return res.json()['AppUserLogin']['FrqShopperNo']


    def try_get_all_coupons(self):
        if self.coupons:
            return
        res = requests.get(self.base_url, headers=self.headers)
        self.coupons = res.json()
        for key in self.coupons.keys():
            print(key)
            self.parse_coupons(key)

        return self.coupons

    def clip(self, coupons):
        if len(coupons) == 0:
            return

        body = _generate_payload(coupons)
        res = requests.post(self.base_url+'/activate', json=body, headers=self.headers)

        if res.status_code <= 299:
            if type(coupons) == type(list()):
                for coupon in coupons:
                    coupon.clipped = True
            else:
                coupons.clipped = True
        else:
            print(f'Clip failed! {res.text}')

    def parse_coupons(self, status):
        coupons = []
        for c in self.coupons[status]:
            coupons.append(Coupon(c, status))
        self.__setattr__(f'{status}_coupons'.lower(), coupons)

    def get_available_coupons(self):
        self.try_get_all_coupons()
        return self.available_coupons

    def get_redeemed_coupons(self):
        self.try_get_all_coupons()
        return self.redeemed_coupons

    def get_activated_coupons(self):
        self.try_get_all_coupons()
        return self.activated_coupons

    def get_expired_coupons(self):
        self.try_get_all_coupons()
        return self.expiredclipped_coupons

class Product:
    def __init__(self, item):
        self.upc = item['UPC']
        self.description = item['Description']
        self.size = item['SizeAlpha']


class Coupon:
    def __init__(self, coupon_json, clipped):
        self._parse_coupon_json(coupon_json, clipped)

    def print_basic_info(self):
        print('\n')
        print('#'*30)
        print(f'Status: {self.status}')
        print(f'Brand: {self.brand_name}')
        print(f'Value: {self.offer_value}')
        print(f'Description: {self.offer_description}')
        print(f'Offer ID: {self.offer_id}')
        print('#' * 30)


    def _parse_coupon_json(self, coupon_json, status):
        self.status = status
        self.clipped = None
        self.offer_id = coupon_json['offerId']
        self.offer_code = coupon_json['offerCode']
        self.offer_description = coupon_json['offerDescription']
        self.offer_value = coupon_json['offerValue'] if 'offerValue' in coupon_json.keys() else None
        self.offer_active_date = coupon_json['offerActiveDate'] if 'offerActiveDate' in coupon_json.keys() else None
        self.offer_expiry_date = coupon_json['offerExpiryDate'] if 'offerExpiryDate' in coupon_json.keys() else None
        self.offer_shutoff_date = coupon_json['offerShutoffDate'] if 'offerShutoffDate' in coupon_json.keys() else None
        self.offer_summary = coupon_json['offerSummary'] if 'offerSummary' in coupon_json.keys() else None
        self.activation_limit = coupon_json['activationLimit'] if 'activationLimit' in coupon_json.keys() else None
        self.brand_name = coupon_json['brandName']
        self.offer_fine_print = coupon_json['offerFinePrint'] if 'offerFinePrint' in coupon_json.keys() else None
        self.offer_disclaimer = coupon_json['offerDisclaimer'] if 'offerDisclaimer' in coupon_json.keys() else None
        self.category_name = coupon_json['categoryName'] if 'categoryName' in coupon_json.keys() else None
        self.offer_disclaimer = coupon_json['offerDisclaimer'] if 'offerDisclaimer' in coupon_json.keys() else None
        self.redemption_limit = coupon_json['redemptionLimit'] if 'redemptionLimit' in coupon_json.keys() else None
        self.min_qty = coupon_json['minQty'] if 'minQty' in coupon_json.keys() else None
        self.items = parse_items(coupon_json['itemDetails']) if 'itemDetails' in coupon_json.keys() else None
        self.redemption_limit = coupon_json['redemptionLimit'] if 'redemptionLimit' in coupon_json.keys() else None


def parse_items(items):
    products = []
    for item in items:
        products.append(Product(item))
    return products


def load_store_info():
    with open('.store_settings', 'r') as file:
        data = json.load(file)
    return data


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
    print(store_json)
    return Store(name=name, store_id=store_id, login_token=login_token)

if __name__ == '__main__':
    stores = []
    for store in load_store_info():
        stores.append(login(store))

    for store in stores:
        coupons = store.get_activated_coupons()
        for x in coupons[:3]:
            x.print_basic_info()
