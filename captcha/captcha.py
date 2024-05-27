from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from ultralytics import YOLO
import cv2
import numpy as np

# 加载模型
# model = yolov5.load('geetestv2.pt', device='cuda:0')
# 测试次数
test_count = 50
# 成功次数
success_count = 0
# 失败次数
failures_count = 0
temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址

for i in range(test_count):
    # 打开浏览器并打开网页
    driver = webdriver.Chrome()
    driver.get("https://www.geetest.com/demo/slide-float.html")

    # 是否可以点击
    is_click = False
    # 图片
    data_url = ""
    # 截图
    screenshot = None
    # 中心 yx轴
    x_center = None
    y_center = None

    # 循环检查直到可以点击为止
    while not is_click:
        try:
            element = driver.find_element(
                By.XPATH, "/html/body/form/div[3]/div/div[3]/div[2]/div[1]/div[3]"
            )
            is_click = True
            # 点击加载验证码
            driver.execute_script("arguments[0].click();", element)
        except NoSuchElementException:
            time.sleep(0.5)

    # 寻找到图片
    while data_url == "":
        try:
            canvas = driver.find_element(
                By.XPATH,
                "/html/body/div/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/div/canvas[1]",
            )
            # 执行JavaScript代码，将canvas转换为dataURL格式的图片数据
            data_url = driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(21);", canvas
            )
            # 对窗口进行截图并保存到本地文件
            screenshot = driver.get_screenshot_as_png()
        except NoSuchElementException:
            time.sleep(0.5)

    # 寻找目标
    if screenshot is not None:

        # 将二进制截图数据转换为图像
        img = cv2.imdecode(np.frombuffer(
            screenshot, np.uint8), cv2.IMREAD_COLOR)
        # 将图像传递给 YOLOv5 模型进行目标检测
        results = model(img)
        # 获取检测到的对象
        detections = results.pandas().xyxy[0]

        for index, detection in detections.iterrows():
            x_center = detection['xmin']
            break
        time.sleep(1)

        # 找到滑动按钮
        distance = 0
        button = None
        while button is None:
            try:
                button = driver.find_element(
                    By.XPATH,
                    "/html/body/div/div[2]/div[1]/div/div[1]/div[2]/div[2]",
                )
                # 计算滑块需要移动的距离 有 5~10的误差
                distance = x_center - button.location['x'] - 9
            except NoSuchElementException:
                time.sleep(0.5)

        # 模拟人类拖动
        actions = ActionChains(driver)
        actions.click_and_hold(button).perform()
        # 如果一直出现 怪物吃了拼图 请重试 问题请看help.py
        actions.move_by_offset(distance, 0).perform()
        time.sleep(1)
        actions.release().perform()
        time.sleep(1)

        # 验证结果
        check_result = driver.find_element(
            By.XPATH,
            '//*[@id="captcha"]/div[3]/div[2]/div[2]/div/div[2]/span[1]',
        )
        if check_result.text == '验证成功':
            success_count += 1
        else:
            failures_count += 1

        driver.quit()

# 输出结果
print(f"验证次数 {test_count} 成功 {success_count} 失败 {failures_count}")
