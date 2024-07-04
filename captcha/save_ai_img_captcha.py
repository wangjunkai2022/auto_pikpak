import os
import time
import requests
import shutil
from pikpak.image import image_run, save_requests_img

file_dir_name = os.path.abspath(os.path.dirname(__file__))


def save_captcha_img():
    url = "https://user.mypikpak.com/pzzl/gen"
    deviceid = "b7742fb931374efe85756ee936da40e5"
    params = {
        "deviceid": deviceid,
        "traceid": ""
    }
    response = requests.get(url, params=params)
    imgs_json = response.json()
    frames = imgs_json["frames"]
    pid = imgs_json['pid']
    traceid = imgs_json['traceid']
    url = "https://user.mypikpak.com/pzzl/image"
    params = {
        'deviceid': deviceid,
        'pid': pid,
        'traceid': traceid
    }
    response1 = requests.get(url, params=params,)
    img_data = response1.content

    # 保存初始图片
    save_requests_img(img_data, os.path.join(file_dir_name, "temp/1.png"))
    # 保存拼图图片
    image_run(os.path.join(file_dir_name, "temp/1.png"), frames)
    # 识别图片
    # ima_path = "temp/"
    # for file in os.listdir(ima_path):
    #     with open(f"{ima_path}/{file}", 'rb') as f:
    #         image_bytes = f.read()
    #         if ai_test_byte(image_bytes) == "ok":
    #             select_id = file.split(".")[0]
    #             break


train_path = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "ai/dataTrain/train")
if __name__ == "__main__":
    # url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    save_captcha_img()
    ima_path = os.path.join(file_dir_name, "temp")
    for file in os.listdir(ima_path):
        shutil.copy(os.path.join(ima_path, file), os.path.join(
            train_path, "bad", str(time.time()) + "_bad.png"))
