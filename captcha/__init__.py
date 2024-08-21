
from captcha.captcha_2captcha import captcha_rewardVip as captcha_2captcha_rewardVip, get_token_register
from captcha.captcha_killer import captcha_rewardVip as captcha_killer_rewardVip, solvev2e_reg
from captcha.captcha_slide_img import captcha


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
        return solvev2e_reg(url)
    except:
        return get_token_register(url)


def google_rewardVip_validation():
    """
    google vip操作
    """
    try:
        return captcha_killer_rewardVip()
    except:
        return captcha_2captcha_rewardVip()
