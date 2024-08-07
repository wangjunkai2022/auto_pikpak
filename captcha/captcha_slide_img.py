import json
import logging
import os

import requests

from captcha.ai.yolov8_test import ai_test_byte
from captcha.captcha_js2py import get_d, img_jj
from captcha.utils import delete_img, extract_parameters, image_run, remove_parameters, save_requests_img


logger = logging.getLogger("slide_img")


def captcha(url: str = ""):
    captcha_url = url
    logger.info('滑块验证中!!!')
    logger.debug(f'url:{url}')
    params_dict = extract_parameters(url)
    # url = remove_parameters(url)
    url = "https://user.mypikpak.com/pzzl/gen"
    device_id = params_dict.get("device_id")
    captcha_token = params_dict.get('captcha_token')
    params = {
        "deviceid": device_id,
        "traceid": ""
    }
    response = requests.get(url, params=params,)
    imgs_json = response.json()
    frames = imgs_json["frames"]
    pid = imgs_json['pid']
    traceid = imgs_json['traceid']
    logger.info('滑块ID:')
    logger.debug(json.dumps(pid, indent=4))
    params = {
        'deviceid': device_id,
        'pid': pid,
        'traceid': traceid
    }
    url = "https://user.mypikpak.com/pzzl/image"
    response1 = requests.get(url, params=params,)
    img_data = response1.content
    tmp_root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_root_path = os.path.join(tmp_root_path, "slide_img_temp")
    one_img = os.path.join(tmp_root_path, "1.png")
    save_requests_img(img_data, one_img)
    # 保存拼图图片
    image_run(one_img, frames)
    # 识别图片
    select_id = None
    for file in os.listdir(tmp_root_path):
        with open(f"{tmp_root_path}/{file}", 'rb') as f:
            image_bytes = f.read()
            if ai_test_byte(image_bytes) == "ok":
                select_id = file.split(".")[0]
                break
    # 删除缓存图片
    delete_img(one_img)
    if not select_id:
        logger.info("ai识别图片失败 重新验证")
        return captcha(captcha_url)
    json_data = img_jj(frames, int(select_id), pid)
    f = json_data['f']
    npac = json_data['ca']
    params = {
        'pid': pid,
        'deviceid': device_id,
        'traceid': traceid,
        'f': f,
        'n': npac[0],
        'p': npac[1],
        'a': npac[2],
        'c': npac[3],
        'd': get_d(pid + device_id + str(f)),
    }
    url = f"https://user.mypikpak.com/pzzl/verify"
    response1 = requests.get(url, params=params,)
    response_data = response1.json()
    if response_data['result'] == 'accept':
        logger.info('验证通过!!!')
        url = f"https://user.mypikpak.com/credit/v1/report?deviceid={device_id}&captcha_token={captcha_token}&type=pzzlSlider&result=0&data={pid}&traceid={traceid}"
        response2 = requests.get(url)
        response_data = response2.json()
        # logger.info('获取验证TOKEN:')
        logger.debug(json.dumps(response_data, indent=4))
        return response_data.get("captcha_token")
    else:
        return ""


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()  # 输出日志到控制台
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # temp_url = "https://user.mypikpak.com/captcha/v2/reCaptcha.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMaHU0YuNiIbD7wSPSL8ZxYckdmcLl6YCQOoAePUFGqKu5VqX2FDUADF_k_3lCdf6HuWumzcilO6T7ZkpJ8Nb0cOhchDmTpUInQ6KfYiT_1Bh6To_L52TY-oQUXVysW_XafqggzLPSaeVgbcFapeTByfcCYJkKerv-5nhu7i1z6KKdiajnuQdbEFpsQDnJqsAjFvVrPJIRkobkX_fq1Jj8qMlLL-KSQCxvGFtql1DUPDqt7Q1U4IuBNLrqXPKwlDmvHlquFvb7o8Kf9wNYeBF8Jj7vWO_jfzVMHw_H3RM3E6iu9R7Skibdvl3GmNv3hbk02y9rYAYXzIsJvjFNH2iJA0cXXdl28dtfuWAb-D-Xg3bP7IAP9fPb6Xta1sqAM5br2KI0_YlzZS0bXl7oFQHbKZxoMGQKpT-QPtai_hnSoi8HsVTCTQ_GJt5EeXr3kLItA.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMZXiDHj2_zheD9GWz5CsaR6xSNMCbl_CHhcWfUdZr3zXG3H5qMwJBLIE4TTw7P4dy54ljpsLDo7s5ecOjS3AZeDHL2e-9rUy74z5HzQ9mHyyjz8lY3hW0voyMjT8tavTLgB7ZAxKmBMi6pXQBynLUZFRlpPLmlF18L6_4Rvuv72n5SVrvith5YTibNGEduK0biN8HUQtrlnEJdyInbMLX2od1zJbJYTLp7reMWsgaG27zRow-mxhRPl8P72vKIf1MMDP5iLb_XtmeEHV3uoPwzeyhi0znC1j_xytF5IaCWDAI3X9eP-xOGxMKAhvy_RjRo_yKCk3-nxVb-La7j19adCVhob1qO4e7EFX-9rYlsks0pimz64RvPi-J1ryapaVDu9FTraiBI6vXSeZfHU9eZu.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&credittype=1&device_id=8bad79d45addb7b4e392f663c3a05467&deviceid=8bad79d45addb7b4e392f663c3a05467&event=xbase-auth-verification&hl=zh&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor"
    # # temp_url = "https://www.google.com/"
    # get_token_register(temp_url)
    # captcha_rewardVip()
    captcha(temp_url)
