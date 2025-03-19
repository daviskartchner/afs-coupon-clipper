# AFSCouponClipper

## Description
This automatically clips all coupons inside certain Associated Food Stores' loyalty sites.

## Prerequisites:

Create the following in the same directory as main.py
- .store_settings
  - Create list of JSON objects with two values: 
  - `[{
    "StoreName": "Store Name",
    "app.js": "https://www.storewebsite.com/_nuxt/app.js"
  }]`
- .login_settings
  - Create with the following data structure:  
    - `{
    "emailOrPhone": "value", 
    "password": "value"
    }`

