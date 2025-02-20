from objects.product import Product


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
        self.items = self.parse_items(coupon_json['itemDetails']) if 'itemDetails' in coupon_json.keys() else None
        self.redemption_limit = coupon_json['redemptionLimit'] if 'redemptionLimit' in coupon_json.keys() else None

    @staticmethod
    def parse_items(items):
        products = []
        for item in items:
            products.append(Product(item))
        return products