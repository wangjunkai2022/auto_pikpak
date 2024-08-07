import logging

import requests
from twocaptcha import TwoCaptcha

from urllib.parse import urlparse, parse_qs, urlunparse
from captcha.utils import extract_parameters, remove_parameters
from config.config import twocapctha_api

logger = logging.getLogger("2captcha")

sitekey_login = "6LdwHgcqAAAAACSTxyrqqnHNY9-NdSvRD-1A1eap"
sitekey_rewardVip = "6LerFi0pAAAAAB8PSfeUmwtJx6imhQpza2dCjMmG"
solver = TwoCaptcha(twocapctha_api)


def get_token_register(url: str = "", data_sitekey=sitekey_login):
    params_dict = extract_parameters(url)
    url = remove_parameters(url)
    result = solver.recaptcha(
        sitekey=data_sitekey,
        url=url,
    )
    logger.info(result)
    url = "https://user.mypikpak.com/credit/v1/report"
    captcha_token = params_dict.get("captcha_token")
    headers = {
        "authority": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        # "cookie": f"captcha_token={captcha_token}"
    }
    params = {
        "deviceid": params_dict["deviceid"],
        'captcha_token': captcha_token,
        'type': "recaptcha",
        "result": '0',
        'data': result['code']

    }

    response = requests.get(url,
                            headers=headers,
                            params=params,
                            )
    res_js_data = response.json()
    # if res_js_data.get("error") != "":
    #     logger.error(res_js_data.get("error"))
    captcha_token = res_js_data.get("captcha_token")
    logger.info(f"自动获得到的token:{captcha_token}")
    return captcha_token


def captcha_rewardVip():
    result = solver.recaptcha(
        sitekey=sitekey_rewardVip,
        # url="https://api-drive.mypikpak.com/vip/v1/verifyRecaptchaToken",
        # url=f"https://www.google.com/recaptcha/api2/userverify?k={sitekey_rewardVip}",
        url="https://user.mypikpak.com"
    )
    logger.info(result)
    return result["code"]


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()  # 输出日志到控制台
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # temp_url = "https://user.mypikpak.com/captcha/v2/reCaptcha.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMaHU0YuNiIbD7wSPSL8ZxYckdmcLl6YCQOoAePUFGqKu5VqX2FDUADF_k_3lCdf6HuWumzcilO6T7ZkpJ8Nb0cOhchDmTpUInQ6KfYiT_1Bh6To_L52TY-oQUXVysW_XafqggzLPSaeVgbcFapeTByfcCYJkKerv-5nhu7i1z6KKdiajnuQdbEFpsQDnJqsAjFvVrPJIRkobkX_fq1Jj8qMlLL-KSQCxvGFtql1DUPDqt7Q1U4IuBNLrqXPKwlDmvHlquFvb7o8Kf9wNYeBF8Jj7vWO_jfzVMHw_H3RM3E6iu9R7Skibdvl3GmNv3hbk02y9rYAYXzIsJvjFNH2iJA0cXXdl28dtfuWAb-D-Xg3bP7IAP9fPb6Xta1sqAM5br2KI0_YlzZS0bXl7oFQHbKZxoMGQKpT-QPtai_hnSoi8HsVTCTQ_GJt5EeXr3kLItA.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMZXiDHj2_zheD9GWz5CsaR6xSNMCbl_CHhcWfUdZr3zXG3H5qMwJBLIE4TTw7P4dy54ljpsLDo7s5ecOjS3AZeDHL2e-9rUy74z5HzQ9mHyyjz8lY3hW0voyMjT8tavTLgB7ZAxKmBMi6pXQBynLUZFRlpPLmlF18L6_4Rvuv72n5SVrvith5YTibNGEduK0biN8HUQtrlnEJdyInbMLX2od1zJbJYTLp7reMWsgaG27zRow-mxhRPl8P72vKIf1MMDP5iLb_XtmeEHV3uoPwzeyhi0znC1j_xytF5IaCWDAI3X9eP-xOGxMKAhvy_RjRo_yKCk3-nxVb-La7j19adCVhob1qO4e7EFX-9rYlsks0pimz64RvPi-J1ryapaVDu9FTraiBI6vXSeZfHU9eZu.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&credittype=1&device_id=8bad79d45addb7b4e392f663c3a05467&deviceid=8bad79d45addb7b4e392f663c3a05467&event=xbase-auth-verification&hl=zh&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor"
    # # temp_url = "https://www.google.com/"
    # get_token_register(temp_url)
    # captcha_rewardVip()
