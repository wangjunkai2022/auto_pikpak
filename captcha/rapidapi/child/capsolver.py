import logging
from captcha.rapidapi.rapidapi import BaseRapidapi

logger = logging.getLogger("rapidapi_capsolver")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class Capsolver(BaseRapidapi):
    api_url = 'https://capsolver.p.rapidapi.com/recaptcha_v2'
    key_api_params_url = "page_url"
    key_api_params_sitekey = 'website_key'
    params = {
        "data": "{\"blob\":\"HERE_COMES_THE_blob_VALUE\"}"
    }