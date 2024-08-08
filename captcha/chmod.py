import logging
import re
from selenium import webdriver
import time

logger = logging.getLogger("captcha_chmod")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def open_url2token(url: str = ""):
    try:
        return _open_url2token(url=url)
    except:
        return open_url2token(url=url)


def _open_url2token(url=""):
    # 设置Chrome浏览器的驱动路径
    driver_path = "chromedriver"  # 请替换为实际的chromedriver路径

    # 创建一个Chrome浏览器实例
    options = webdriver.ChromeOptions()
    options.add_argument("--enable-logging")  # 开启控制台日志
    service = webdriver.ChromeService()
    service.executable_path = driver_path
    # options.add_argument("--headless")  # 以无头模式运行，不显示浏览器窗口
    driver = webdriver.Chrome(service=service, options=options)
    # 打开指定的网页
    driver.get(url)
    captured_url = ""
    while True:
        time.sleep(0.1)
        logs = driver.get_log("browser")
        # 遍历日志并提取指定错误信息
        for log in logs:
            if log["level"] == "SEVERE" and "Failed to launch" in log["message"]:
                error_message = log["message"]
                # 在这里可以将错误信息保存到文件或进行其他处理
                print(error_message)
                captured_url = error_message
        if captured_url != "":
            break

    # 关闭浏览器
    driver.quit()
    str_start = "captcha_token="
    str_end = "&expires_in"
    search = re.search(f"{str_start}.*{str_end}", captured_url)
    captcha_token = search.group()[len(str_start):-len(str_end)]
    logger.debug(f"运行后的获取到的 captcha_token:\n{captcha_token}")
    return captcha_token


if __name__ == "__main__":
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    temp_url = "https://user.mypikpak.com/captcha/v2/reCaptcha.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMaHU0YuNiIbD7wSPSL8ZxYckdmcLl6YCQOoAePUFGqKu5VqX2FDUADF_k_3lCdf6HuWumzcilO6T7ZkpJ8Nb0cOhchDmTpUInQ6KfYiT_1Bh6To_L52TY-oQUXVysW_XafqggzLPSaeVgbcFapeTByfcCYJkKerv-5nhu7i1z6KKdiajnuQdbEFpsQDnJqsAjFvVrPJIRkobkX_fq1Jj8qMlLL-KSQCxvGFtql1DUPDqt7Q1U4IuBNLrqXPKwlDmvHlquFvb7o8Kf9wNYeBF8Jj7vWO_jfzVMHw_H3RM3E6iu9R7Skibdvl3GmNv3hbk02y9rYAYXzIsJvjFNH2iJA0cXXdl28dtfuWAb-D-Xg3bP7IAP9fPb6Xta1sqAM5br2KI0_YlzZS0bXl7oFQHbKZxoMGQKpT-QPtai_hnSoi8HsVTCTQ_GJt5EeXr3kLItA.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMZXiDHj2_zheD9GWz5CsaR6xSNMCbl_CHhcWfUdZr3zXG3H5qMwJBLIE4TTw7P4dy54ljpsLDo7s5ecOjS3AZeDHL2e-9rUy74z5HzQ9mHyyjz8lY3hW0voyMjT8tavTLgB7ZAxKmBMi6pXQBynLUZFRlpPLmlF18L6_4Rvuv72n5SVrvith5YTibNGEduK0biN8HUQtrlnEJdyInbMLX2od1zJbJYTLp7reMWsgaG27zRow-mxhRPl8P72vKIf1MMDP5iLb_XtmeEHV3uoPwzeyhi0znC1j_xytF5IaCWDAI3X9eP-xOGxMKAhvy_RjRo_yKCk3-nxVb-La7j19adCVhob1qO4e7EFX-9rYlsks0pimz64RvPi-J1ryapaVDu9FTraiBI6vXSeZfHU9eZu.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&credittype=1&device_id=8bad79d45addb7b4e392f663c3a05467&deviceid=8bad79d45addb7b4e392f663c3a05467&event=xbase-auth-verification&hl=zh&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor"
    # temp_url = "https://www.google.com/"
    open_url2token(temp_url)
