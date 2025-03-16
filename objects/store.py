import requests
import json

from objects.coupon import Coupon
from logger import Logger as StoreLogger


def get_login_credentials():
    with open('.login_settings', 'r') as file:
        return json.load(file)


def generate_payload(coupons):
    if type(coupons) == type(list()):
        offer_ids = []
        for coupon in coupons:
            offer_ids.append(coupon.offer_id)
    else:
        offer_ids = coupons.offer_id
    return {'offers': offer_ids}


class Store:
    def __init__(self, name, store_id, login_token):
        self._logger = StoreLogger(name)
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
        if res.status_code >= 299:
            raise Exception
        self._logger.log('Successfully logged in')
        return res.json()['AppUserLogin']['FrqShopperNo']

    def try_get_all_coupons(self):
        if self.coupons:
            return self.coupons
        return self.force_get_coupons()

    def force_get_coupons(self):
        res = requests.get(self.base_url, headers=self.headers)
        self.coupons = res.json()
        for key in self.coupons.keys():
            self.parse_coupons(key)
        self.log_coupon_summary()
        return self.coupons

    def clip(self, coupons):
        if len(coupons) == 0:
            self._logger.log('No coupons available to clip')
            return

        body = generate_payload(coupons)
        self._logger.log('Clipping {0}'.format(body))
        res = requests.post(self.base_url + '/activate', json=body, headers=self.headers)
        self._logger.log('Response code: {0}'.format(res.status_code))
        if res.status_code <= 299 and 'failure' not in res.json().keys():
            if type(coupons) == type(list()):
                for coupon in coupons:
                    coupon.clipped = True
            else:
                coupons.clipped = True
        else:
            self._logger.log(f'Clip failed! {res.text}')

        self.force_get_coupons()

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

    def get_coupon_summary(self):
        self.log_coupon_summary()
        print('#' * (len(self.name)+(18*2)))
        print(f"{'#'*15}   {self.name}   {'#'*15}")
        print(f'\t\t\t{len(self.activated_coupons)} clipped coupons'.upper())
        print(f'\t\t\t{len(self.available_coupons)} available coupons'.upper())
        print(f'\t\t\t{len(self.redeemed_coupons)} redeemed coupons'.upper())
        print(f'\t\t\t{len(self.expiredclipped_coupons)} expired coupons'.upper())
        print('#' * (len(self.name)+(18*2)))

    def log_coupon_summary(self):
        log_value = '{0} available coupons | {1} clipped coupons'.format(len(self.available_coupons), len(self.activated_coupons))
        self._logger.log(log_value)

