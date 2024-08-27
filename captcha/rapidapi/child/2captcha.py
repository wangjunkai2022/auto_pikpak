import logging
from captcha.rapidapi.rapidapi import BaseRapidapi

logger = logging.getLogger("rapidapi_2captcha")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class Captcha2(BaseRapidapi):
    api_url = 'https://2captcha4.p.rapidapi.com/recaptcha_v2'
    key_api_params_url = "page_url"
    key_api_params_sitekey = 'google_key'
