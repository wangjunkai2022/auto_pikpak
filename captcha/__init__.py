
import logging
from captcha.captcha_2captcha import captcha_rewardVip as captcha_2captcha_rewardVip, get_token_register
from captcha.captcha_slide_img import captcha
from captcha.rapidapi.rapidapi import create_instance_and_pikpak_req, create_instance_and_pikpak_rewardVip

logger = logging.getLogger("captcha")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def slider_validation(url: str):
    """
    滑块验证
    """
    return captcha(url)


def google_re_validation(url: str):
    """
    google 注册验证
    """
    try:
        return create_instance_and_pikpak_req(url)
    except Exception as e:
        return get_token_register(url)


def google_rewardVip_validation():
    """
    google vip操作
    """
    try:
        return create_instance_and_pikpak_rewardVip()
    except Exception as e:
        return captcha_2captcha_rewardVip()
