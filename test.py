# coding: utf-8
__author__ = 'Mancuniancol'

import requests

browser = requests.session()

url = "https://thepiratebay.se/"

response = browser.get(url)

print response.status_code
print response.text
