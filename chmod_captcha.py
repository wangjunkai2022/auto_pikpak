import base64
import random
import re
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import threading
import os

import yolov8_test

import pytweening

train_path = "./dataTrain/train"
oldAllImg = []
for root, dir, _file in os.walk(train_path):
    for file in _file:
        if "png" in file:
            with open(os.path.join(root, file), "rb") as imagefile:
                convert = imagefile.read()
            isHave = False
            for img in oldAllImg:
                if img == convert:
                    isHave = True
                    break
            if not isHave:
                oldAllImg.append(convert)

newAllImg = []

# 判断img文件是否已经列表中了


def CheckImgBase64ToList(img):
    if img in oldAllImg:
        return True
    if img in newAllImg:
        return True

    return False

# 保存所有文件到文件系统中


def SaveAllNewImg(ok_img):
    for img in newAllImg:
        saveImg(img, img == ok_img)

# 保存文件到AI学习环境


def saveImg(img, isOk):
    file = open(
        f'{train_path}/{isOk and "ok" or "bad"}/{time.time()}_{isOk and "ok" or "bad"}.png', "wb")
    file.write(img)
    file.close()
    time.sleep(1)


class Captcha_Chmod:
    captured_url = ''
    driver = None
    captcha_token = ''
    image = None

    def __init__(self, url=""):
        driver_path = "chromedriver"  # 请替换为实际的chromedriver路径
        # 创建一个Chrome浏览器实例
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService()
        service.executable_path = driver_path
        # options.add_argument("--headless")  # 以无头模式运行，不显示浏览器窗口
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)

        self.driver.get(url)

        self.runingTh = threading.Thread(target=self.__th_get_captured_url)
        self.runingTh.start()
        # self.saveImage()
        self.touchTh = threading.Thread(target=self.__th_touch_slider__button)
        self.touchTh.start()

        self.printTh = threading.Thread(target=self.__print_button_info)
        self.printTh.start()

        # self.runingTh.join()

    # 新线程获取验证
    def __th_get_captured_url(self):
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
        self.driver.execute_script(script)

        while True:
            time.sleep(1)

            try:
                self.captured_url = self.driver.execute_script(
                    "return lastLog2;")
                if self.captured_url.startswith("xlaccsdk01"):
                    break
                # print(f"值:{self.captured_url}不对")
            except Exception as e:
                if "HTTPConnectionPool" in e.__str__():
                    # if isinstance(e, HTTPConnectionPool):
                    # print("关闭了")
                    break
                # print(f"没有值{e}")
                pass
        print(f"获取到了验证信息{self.captured_url}")
        self.saveImage()
        self.driver.quit()
        str_start = "captcha_token="
        str_end = "&expires_in"
        search = re.search(f"{str_start}.*{str_end}", self.captured_url)
        self.captcha_token = search.group()[len(str_start):-len(str_end)]
        print(f"运行后的获取到的 captcha_token:\n{self.captcha_token}")
        return self.captcha_token

    def drag_and_drop(browser, offset):
        pytweening.easeInOutElastic()
        # ActionChains(browser).pause(0.5).release().perform()

    def __th_touch_slider__button(self):
        button = self.driver.find_element(by=By.ID, value="slider__button")
        actions = ActionChains(self.driver)
        actions.click_and_hold(button).perform()
        distance = button.location_once_scrolled_into_view
        x, y = distance.get("x"), 0
        print(x, y)
        while True:
            try:
                x += random.randint(2, 6)
                actions.move_by_offset(x, y).perform()
                if self.saveImage():
                    print("当前移动的X:", x)
                    if yolov8_test.ai_test_byte(self.image) == "ok":
                        print("AI 判断通过")
                        actions.release().perform()
                        return
                    # time.sleep(random.random())
                    time.sleep(random.uniform(0, 0.2))
                time.sleep(random.uniform(0, 0.5))
            except:
                print("报错：：：：")
                ActionChains(self.driver).click_and_hold(
                    button).move_by_offset(distance.get("x"), y).release().perform()
                break
        print("循环结束应该已经到最后位置了")
        # actions.release().perform()
        ActionChains(self.driver).pause(0.5).release().perform()
        # self.driver.quit()

    def __print_button_info(self):
        button = self.driver.find_element(by=By.ID, value="slider__button")
        oldPos = button.location_once_scrolled_into_view
        while True:
            if button.location_once_scrolled_into_view != oldPos:
                oldPos = button.location_once_scrolled_into_view
                print(button.location_once_scrolled_into_view, "::::", time.time())

    def saveImage(self):
        canvas = self.driver.find_element(by=By.ID, value="pzzl-canvas")
        # 执行JavaScript代码，将canvas转换为dataURL格式的图片数据
        canvas_data = self.driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(21);", canvas
        )
        # 对窗口进行截图并保存到本地文件
        # screenshot = driver.get_screenshot_as_base64()
        self.image = base64.b64decode(canvas_data)
        if CheckImgBase64ToList(self.image):
            return False
        newAllImg.append(self.image)
        return True


def open_url2token(url):
    captcha = Captcha_Chmod(url)
    print(captcha.captcha_token)
    if captcha.captcha_token:
        SaveAllNewImg(captcha.image)
    newAllImg.clear()


if __name__ == "__main__":
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # # temp_url = "https://www.google.com/"
    # # open_url2token(temp_url)
    # captcha = Captcha_Chmod(temp_url)
    # print(captcha.captcha_token)
    # if captcha.captcha_token:
    #     SaveAllNewImg(captcha.image)
    # newAllImg.clear()
    while True:
        print(random.uniform(0, 0.3))
