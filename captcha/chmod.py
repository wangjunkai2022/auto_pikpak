import logging
import re
from selenium import webdriver
import time

logger = logging.getLogger("captcha_chmod")


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
    service = webdriver.ChromeService()
    service.executable_path = driver_path
    # options.add_argument("--headless")  # 以无头模式运行，不显示浏览器窗口
    driver = webdriver.Chrome(service=service, options=options)
    # 打开指定的网页

    driver.get(url)
    # 注入JavaScript脚本以捕获window.location.replace(d)的值
    # script = """
    # py_myUrl="";
    # window.onbeforeunload = function(e) {
    #     py_myUrl = window.location.href
    #     console.log("URL即将更改:", window.location.href,"eeeee",e);
    # };
    # """
    script = '''
        lastLog = "";
        lastLog2 = "";
        console.oldLog = console.log;
        console.log = function(str,str2) {
          console.oldLog(str);
          lastLog = str;
          lastLog2 = str2;
        }
    '''
    driver.execute_script(script)
    # 获取捕获的URL值
    captured_url = driver.execute_script("return lastLog;")
    logger.debug("捕获的URL:", captured_url)

    while True:
        time.sleep(0.1)
        try:
            captured_url = driver.execute_script("return lastLog2;")
            if captured_url.startswith("xlaccsdk01"):
                break
        except Exception as e:
            logger.debug("报错了", e)
            driver.quit()
            return open_url2token(url=url)
        # message = driver.get_log("performance")
        # logger.debug(message)
        # logger.debug(f"当前网页是：{driver.current_url}")
    # 关闭浏览器
    driver.quit()
    str_start = "captcha_token="
    str_end = "&expires_in"
    search = re.search(f"{str_start}.*{str_end}", captured_url)
    captcha_token = search.group()[len(str_start):-len(str_end)]
    logger.debug(f"运行后的获取到的 captcha_token:\n{captcha_token}")
    return captcha_token


if __name__ == "__main__":
    temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # temp_url = "https://www.google.com/"
    open_url2token(temp_url)
