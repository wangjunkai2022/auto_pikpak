import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import uuid

import requests
from captcha.captcha_2captcha import captcha_rewardVip, get_token_register
from captcha.captcha_slide_img import captcha

logger = logging.getLogger("Chrome_Pikpak")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Handle():
    def __def_getTonek(self, url: str = ""):
        token_input = input(f"验证url: {url} \n请输入获取到的token并按回车结束\n")
        return token_input

    def __def_get_mailcode(self, mail: str = ''):
        code = input(f'输入 {mail} 邮箱中收到的验证码:\n')
        return code

    __get_token_callback = None
    __get_mailcode_callback = None

    def __init__(self, get_token=None, get_mailcode=None) -> None:
        self.__get_token_callback = get_token or self.__def_getTonek
        self.__get_mailcode_callback = get_mailcode or self.__def_get_mailcode

    def run_get_token(self, url):
        return self.__get_token_callback(url)

    def run_get_maincode(self, mail):
        return self.__get_mailcode_callback(mail)


DEF_AUTHORIZATION = "def_authorization"
DEF_CAPTCHATOKEN = "def_captcha_token"
DEF_USERID = 'def_user_id'


class ChromePikpak():
    mail = ""
    pd = ""
    device_id = None
    authorization = DEF_AUTHORIZATION
    captcha_token = DEF_CAPTCHATOKEN
    user_id = DEF_USERID

    proxies = None

    CLIENT_ID = 'YUMx5nI8ZU8Ap8pm'
    CLIENT_VERSION = '2.0.0'

    # 网络连接重试状态码
    RETRY_STATUS_CODE = [502]

    handler: Handle = Handle()
    old_captcha_token = None

    # 当前可以领取的vip活动
    vip_active = {
        'bot_checked': False,
        "install_web_pikpak_extension": False,
        "upload_file": False
    }

    def __init__(self, mail: str, pd: str,):
        self.mail = mail
        self.pd = pd
        self.device_id = str(uuid.uuid4()).replace("-", "")

    def setHandler(self, handler: Handle = Handle()):
        self.handler = handler

    cache_json_file = os.path.abspath(__file__)[:-3] + "user" + ".json"

    def save_self(self):
        try:
            with open(self.cache_json_file, mode="r", encoding="utf-8") as file:
                json_str = file.read()
                json_data = json.loads(json_str)
        except:
            json_data = {}

        json_data[self.mail] = {
            "captcha_token": self.captcha_token,
            'authorization': self.authorization,
            'user_id': self.user_id,
            'proxies': self.proxies,
            'device_id': self.device_id,
            'password': self.pd,
        }
        with open(self.cache_json_file, mode='w', encoding="utf-8") as file:
            file.write(json.dumps(json_data, indent=4, ensure_ascii=False))

    def read_self(self):
        try:
            with open(self.cache_json_file, mode="r", encoding="utf-8") as file:
                json_str = file.read()
                json_data = json.loads(json_str)
        except:
            json_data = {}
        data = json_data.get(self.mail)
        if data:
            self.captcha_token = data['captcha_token']
            self.authorization = data['authorization']
            self.user_id = data['user_id']
            self.proxies = data['proxies']
            self.device_id = data['device_id']
            self.pd = data['password']

    def set_proxy(self, proxy_ip, type="http"):
        # if not proxy.startswith("http://"):
        if not proxy_ip:
            self.proxies = None
            return
        proxy = f"{type}://{proxy_ip}"
        self.proxies = {
            "http": proxy,
            "https": proxy,
        }

    # 仿制captcha_sign
    def __get_sign(self, time_str):
        begin_str = self.CLIENT_ID + \
            f"{self.CLIENT_VERSION}mypikpak.com" + \
            self.device_id + time_str
        salts = [
            {'alg': "md5", 'salt': "C9qPpZLN8ucRTaTiUMWYS9cQvWOE"},
            {'alg': "md5", 'salt': "+r6CQVxjzJV6LCV"},
            {'alg': "md5", 'salt': "F"},
            {'alg': "md5", 'salt': "pFJRC"},
            {'alg': "md5", 'salt': "9WXYIDGrwTCz2OiVlgZa90qpECPD6olt"},
            {'alg': "md5", 'salt': "/750aCr4lm/Sly/c"},
            {'alg': "md5", 'salt': "RB+DT/gZCrbV"},
            {'alg': "md5", 'salt': ""},
            {'alg': "md5", 'salt': "CyLsf7hdkIRxRm215hl"},
            {'alg': "md5", 'salt': "7xHvLi2tOYP0Y92b"},
            {'alg': "md5", 'salt': "ZGTXXxu8E/MIWaEDB+Sm/"},
            {'alg': "md5", 'salt': "1UI3"},
            {'alg': "md5", 'salt': "E7fP5Pfijd+7K+t6Tg/NhuLq0eEUVChpJSkrKxpO"},
            {'alg': "md5", 'salt': "ihtqpG6FMt65+Xk+tWUH2"},
            {'alg': "md5", 'salt': "NhXXU9rg4XXdzo7u5o"}
        ]

        hex_str = begin_str
        for index in range(len(salts)):
            optJSONObject = salts[index]
            if optJSONObject is not None:
                optString = optJSONObject.get("alg", "")
                optString2 = optJSONObject.get("salt", "")
                if optString == "md5":
                    # 使用md5算法对字符串进行加密
                    hex_str = hashlib.md5(
                        (hex_str + optString2).encode()).hexdigest()
        return hex_str

    def captcha(self, action: str = ''):
        self.old_captcha_token = self.captcha_token
        time_str = str(round(time.time() * 1000))
        if self.authorization and self.authorization != "":
            def_bodys = {
                "client_id": self.CLIENT_ID,
                "action": action,
                "device_id": self.device_id,
                "captcha_token": self.captcha_token,
                "meta": {
                    "captcha_sign": f"1.{self.__get_sign(time_str)}",
                    "client_version": self.CLIENT_VERSION,
                    "package_name": "mypikpak.com",
                    "user_id": self.user_id,
                    "timestamp": time_str

                }
            }
        else:
            def_bodys = {
                "client_id": self.CLIENT_ID,
                "action": action,
                "device_id": self.device_id,
                "meta": {
                    "email": self.mail
                }
            }
        bodys = {
            "POST:/v1/auth/signin": {
                "client_id": self.CLIENT_ID,
                "action": 'POST:/v1/auth/signin',
                "device_id": self.device_id,
                "meta": {
                    "email": self.mail
                }
            },
            'POST:/v1/auth/verification': {
                "client_id": self.CLIENT_ID,
                "action": "POST:/v1/auth/verification",
                "device_id": self.device_id,
                "captcha_token": self.captcha_token,
                "meta": {
                    "email": self.mail,
                }
            }

        }
        body = bodys.get(action) or def_bodys
        url = 'https://user.mypikpak.com/v1/shield/captcha/init'
        json_data = self.post(url, json=body)
        if json_data.get("url"):
            self.captcha_token = json_data.get("captcha_token")
            expires_in = json_data.get("expires_in")
            start_time = time.time()
            recaptcha_url: str = json_data.get("url")
            isOk = False
            if "spritePuzzle.html" in recaptcha_url:
                # 官网修改了注册验证方式。这个滑块验证现在登陆时还在用
                while (time.time() - start_time) < expires_in * (3/4):
                    captcha_token = captcha(recaptcha_url)
                    if captcha_token != "":
                        self.captcha_token = captcha_token
                        isOk = True
                        break
            elif "reCaptcha.html" in recaptcha_url:
                self.captcha_token = get_token_register(recaptcha_url)
                isOk = True
            if isOk:
                pass
            else:
                self.captcha_token = self.handler and self.handler.run_get_token(
                    recaptcha_url)
        else:
            error = json_data.get("error")
            if error:
                raise Exception(error)
            self.captcha_token = json_data.get("captcha_token")

    def _requests(self, method: str, url: str, headers=None, **kwargs):
        headers = headers or self.headers(url)
        for count in range(0, 3):
            try:
                response = requests.request(method, url, headers=headers,
                                            proxies=self.proxies, verify=False, **kwargs)
            except Exception as e:
                logger.error(f"{method}请求报错了{e}\nresponse:{response}")
                time.sleep(2)
                logger.error(f"{method}请求正在重试{count}/3")
                continue
            if response.status_code == 200:
                break
            elif response.status_code in self.RETRY_STATUS_CODE:
                logger.error(f"请求报错了等待重试 {response}")
                time.sleep(5)
            else:
                logger.debug(f"正常吗？{response}")
                break
        json_data = response.json()
        error = json_data.get("error")
        if error and (error == "captcha_invalid" or error == "captcha_required"):
            # 使用 urlparse 解析 URL
            parsed_url = urlparse(url)
            # 获取域名和路径
            domain = parsed_url.netloc  # 域名，包括端口（如果有）
            path = parsed_url.path      # 路径
            old_capctah = self.captcha_token
            self.captcha(f"{method.upper()}:{path}")
            self._change_request_values(
                old_capctah, self.captcha_token, headers, **kwargs)
            return self._requests(method, url, headers, **kwargs)
        elif error and error == 'unauthenticated':
            self.authorization = DEF_AUTHORIZATION
            old_capctah = self.captcha_token
            old_authorization = self.authorization
            self.save_self()
            self.login()
            self._change_request_values(
                old_capctah, self.captcha_token, headers, **kwargs)
            self._change_request_values(
                old_authorization, self.authorization, headers, **kwargs)
            return self._requests(method, url, headers, **kwargs)
        if error and error != '':
            raise Exception(error)
        return json_data

    def get(self, url, headers=None, **kwargs):
        return self._requests("get", url, headers, **kwargs)

    def post(self, url, headers=None, **kwargs):
        return self._requests("post", url, headers, **kwargs)

    def _change_request_values(self, old_value, new_value, headers: dict = None, **kwargs):
        logger.debug(f"原来的 headers :\n{headers}")
        for key, value in headers.items():
            if value == old_value:
                headers[key] = new_value

        logger.debug(f"打印修改后的 headers :\n{headers}")

        logger.debug(f"原来的 kwargs :\n{kwargs}")
        # 遍历 kwargs 中的所有项
        for key, value in kwargs.items():
            # 检查值是否为字典
            if isinstance(value, dict):
                # 遍历字典中的键值对
                for k, v in value.items():
                    # 如果字典中的值等于目标字符，则进行修改
                    if v == old_value:
                        value[k] = new_value  # 修改为新的值

        # 打印修改后的 kwargs，用于验证
        logger.debug(f'打印修改后的 kwargs，用于验证:\n{kwargs}')

    def headers(self, url: str):
        # 解析 URL
        parsed_url = urlparse(url)

        # 获取主机名
        hostname = parsed_url.hostname
        # 分割主机名并提取二级域名
        if hostname:
            parts = hostname.split('.')
            if len(parts) >= 3:  # 确保有足够的部分
                second_level_domain = parts[-3]  # 倒数第三个部分
                logger.debug(f'二级域名: {second_level_domain}')
        header_config = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN',
            'authorization': self.authorization,
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://mypikpak.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://mypikpak.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-captcha-token': self.captcha_token,
            'x-device-id': self.device_id,
        }

        header_user = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://mypikpak.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://mypikpak.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-captcha-token': self.captcha_token,
            'x-client-id': self.CLIENT_ID,
            'x-client-version': '1.0.0',
            'x-device-id': self.device_id,
            'x-device-model': 'chrome%2F127.0.0.0',
            'x-device-name': 'PC-Chrome',
            'x-device-sign': f'wdi10.{self.device_id}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'x-net-work-type': 'NONE',
            'x-os-version': 'MacIntel',
            'x-platform-version': '1',
            'x-protocol-version': '301',
            'x-provider-name': 'NONE',
            'x-sdk-version': '8.0.3',

            'authorization': self.authorization,
        }

        headers = {
            'config': header_config,
            "api-drive": header_config,
            "user": header_user,
        }
        return headers.get(second_level_domain)

    # 注册
    def register(self):
        # self.captcha("POST:/v1/auth/verification")
        url = 'https://user.mypikpak.com/v1/auth/verification'
        json_data = {
            "email": self.mail,
            "target": "ANY",
            "usage": "REGISTER",
            "locale": "zh-CN",
            "client_id": self.CLIENT_ID
        }
        json_data = self.post(url, json=json_data)
        logger.debug(f"verification 数据{json_data}")
        verification_id = json_data.get("verification_id")
        if verification_id:
            pass
        else:
            raise Exception(json_data.get('error'))
        code = self.handler.run_get_maincode(self.mail)
        url = f"https://user.mypikpak.com/v1/auth/verification/verify"
        payload = {
            "client_id": self.CLIENT_ID,
            "verification_id": verification_id,
            "verification_code": code,
        }
        json_data = self.post(url, json=payload)
        logger.debug(f"verification/verify 数据{json_data}")
        verification_token = json_data.get('verification_token')
        if verification_token and verification_token != "":
            pass
        else:
            raise Exception(json_data.get('error'))

        url = f"https://user.mypikpak.com/v1/auth/signup"
        payload = {
            "email": self.mail,
            "verification_code": code,
            "verification_token": verification_token,
            "password": self.pd,
            "client_id": self.CLIENT_ID
        }
        json_data = self.post(url, json=payload)
        logger.debug(f"signup 数据{json_data}")
        if json_data.get('error'):
            raise Exception(json_data.get('error'))
        self.user_id = json_data.get('sub')
        self.authorization = f"{json_data.get('token_type')} {json_data.get('access_token')}"
        self.save_self()

    def login(self):
        self.read_self()
        if self.authorization != DEF_AUTHORIZATION:
            logger.debug("已经登陆了")
            return
        url = "https://user.mypikpak.com/v1/auth/signin"
        body = {
            "username": self.mail,
            "password": self.pd,
            "client_id": self.CLIENT_ID,
        }
        json_data = self.post(url, json=body)
        if not json_data.get('error'):
            logger.debug(f"登陆成功{json_data}")
            self.user_id = json_data.get("sub")
            self.authorization = f"{json_data.get('token_type')} {json_data.get('access_token')}"
            self.save_self()
        else:
            error_str = json_data.get("error")
            if error_str == "captcha_required" or error_str == "captcha_invalid":
                captcha_action = "POST:/v1/auth/signin"
                self.captcha(captcha_action)
                self.login()
                return
            logger.error(f"登陆失败{json_data}")
            raise Exception(error_str)

    def me(self):
        url = 'https://user.mypikpak.com/v1/user/me'
        payload = {
            "sub": "",
            "name": self.mail.split('@')[0],
            "email": self.mail,
            "password": "SET",
            "created_at": "",
            "password_updated_at": "",
        }
        headers = {'accept': '*/*',
                   'accept-encoding': 'gzip, deflate, br, zstd',
                   'accept-language': 'zh-CN',
                   'authorization': self.authorization,
                   'cache-control': 'no-cache',
                   'content-type': 'application/json',
                   'origin': 'https://mypikpak.com',
                   'pragma': 'no-cache',
                   'priority': 'u=1, i',
                   'referer': 'https://mypikpak.com/',
                   'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                   'sec-ch-ua-mobile': '?0',
                   'sec-ch-ua-platform': '"macOS"',
                   'sec-fetch-dest': 'empty',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site': 'same-site',
                   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                   'x-captcha-token': self.captcha_token,
                   'x-client-id': self.CLIENT_ID,
                   'x-client-version': '1.0.0',
                   'x-device-id': self.device_id,
                   'x-device-model': 'chrome%2F127.0.0.0',
                   'x-device-name': 'PC-Chrome',
                   'x-device-sign': f'wdi10.{self.device_id}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                   'x-net-work-type': 'NONE',
                   'x-os-version': 'MacIntel',
                   'x-platform-version': '1',
                   'x-protocol-version': '301',
                   'x-provider-name': 'NONE',
                   'x-sdk-version': '8.0.3', }
        json_data = self.get(url, params=payload)
        logger.debug(f"自己的数据{json_data}")

    def configs(self):
        payload = {
            "client": "web",
            "data": {
                "language_system": "zh-CN",
                "language_app": "zh-CN",
                "user_id": self.user_id,
            }
        }
        url = 'https://config.mypikpak.com/config/v1/basic'
        json_data = self.post(url, json=payload)
        logger.debug(f"config_basic{json_data}")

        url = 'https://api-drive.mypikpak.com/operating/v1/content'
        json_data = self.post(url, json=payload)
        logger.debug(f"operating_content::{json_data}")

        url = 'https://config.mypikpak.com/config/v1/drive'
        json_data = self.post(url, json=payload)
        logger.debug(f"config_drive:{json_data}")

        url = 'https://config.mypikpak.com/config/v1/activity_operation'
        json_data = self.post(url, json=payload)
        logger.debug(f"config_activity_operation:{json_data}")

    def lbsInfo(self):
        url = 'https://access.mypikpak.com/access_controller/v1/lbsInfo'
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN',
            'cache-control': 'no-cache',
            'connection': 'keep-alive',
            'content-type': 'application/json',
            'host': 'access.mypikpak.com',
            'origin': 'https://mypikpak.com',
            'pragma': 'no-cache',
            'referer': 'https://mypikpak.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-client-id': self.CLIENT_ID,
            'x-device-id': self.device_id,
        }
        json_data = self.get(url, headers=headers)
        logger.debug(f"libsinfo:{json_data}")

    def user_settings_bookmark(self):
        url = 'https://api-drive.mypikpak.com/user/v1/settings'
        json_data = self.get(url, params={
            "items": 'bookmark',
        })
        logger.debug(f"user_settings_bookmark:{json_data}")

    def about(self):
        url = 'https://api-drive.mypikpak.com/drive/v1/about?'
        json_data = self.get(url)
        logger.debug(f"about:{json_data}")

    def inviteCode(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/inviteCode'
        json_data = self.get(url)
        logger.debug(f"inviteCode:{json_data}")
        return json_data

    def vip_checkInvite(self):
        url = f'https://api-drive.mypikpak.com/vip/v1/activity/checkInvite'
        params = {
            'userid': self.user_id
        }
        json_data = self.get(url, params=params)
        logger.debug(f"vip_checkInvite:{json_data}")

    def vip_info(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/vip/info'
        json_data = self.get(url)
        logger.debug(f"vip_info:{json_data}")
        return json_data

    def vip_inviteList(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/inviteList?limit=500'
        json_data = self.get(url)
        logger.debug(f"vip_inviteList:{json_data}")

    # 活动检测
    def check_task_status(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/task/status:batchGet?scene=upload_file&scene=install_web_pikpak_extension'
        json_data = self.get(url)
        logger.debug(f"task_status:{json_data}")
        data = json_data.get('data')
        if data:
            for key, value in data.items():
                self.vip_active['bot_checked'] = value.get("bot_checked")
                self.vip_active[key] = value.get('result') != 'success'

    def upgradeToPro(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/upgradeToPro'
        json_data = self.get(url)
        logger.debug(f"upgradeToPro:{json_data}")

    def inviteInfo(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/inviteInfo'
        json_data = self.get(url)
        logger.debug(f"inviteInfo:{json_data}")

    def task_free_vip(self):
        # url = 'https://api-drive.mypikpak.com/vip/v1/task/status?scene=free_vip'
        # json_data = self.get(url)
        # logger.debug(f"free_vip:{json_data}")
        self.task_status({
            'scene': 'free_vip'
        })

    def task_upload_file(self):
        self.task_status({
            'scene': 'upload_file'
        })

    def task_status(self, params: dict = {}):
        url = 'https://api-drive.mypikpak.com/vip/v1/task/status'
        json_data = self.get(url, params=params)
        logger.debug(f"task_status{params} :{json_data}")

    def task_reference_resource(self):
        url = 'https://api-drive.mypikpak.com/drive/v1/tasks'
        params = {
            "with": "reference_resource",
            "type": "offline",
            "thumbnail_size": "SIZE_SMALL",
            "limit": 10000,
            "filters": '{"phase":{"in":"PHASE_TYPE_COMPLETE"}}',
            "page_token": ""  # 留空的 page_token
        }
        json_data = self.get(url, params=params)

        logger.debug(f"task_reference_resource:{json_data}")

    def invite(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/invite'
        json_data = self.post(url, json={
            "from": "web"
        })
        logger.debug(f"invite:{json_data}")

    # 任务人机验证
    def verifyRecaptchaToken(self):
        self.check_task_status()
        if self.vip_active.get("bot_checked"):
            logger.debug("机器验证已经通过这里不用在次验证了")
            return
        captcha_token = captcha_rewardVip()
        url = 'https://api-drive.mypikpak.com/vip/v1/verifyRecaptchaToken'
        payload = {
            "type": "upload_file",
            "captcha_token": captcha_token,
        }
        json_data = self.post(url, json=payload)
        logger.debug(f"verifyRecaptchaToken:{json_data}")

    def _reward_vip(self, type: str = ''):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/rewardVip'
        payload = {
            "type": type
        }
        json_data = self.post(url, json=payload)
        logger.debug(f"rewardVip {type}:{json_data}")
        self.task_status({
            'scene': type
        })

    # 领取下载活动会员
    def reward_vip_upload_file(self):
        if self.vip_active.get("bot_checked") and self.vip_active.get('upload_file'):
            self._reward_vip('upload_file')

    # 领取安装扩展活动会员
    def reward_vip_install_web_pikpak_extension(self):
        if self.vip_active.get("bot_checked") and self.vip_active.get('install_web_pikpak_extension'):
            self._reward_vip('install_web_pikpak_extension')

    def save_share_2_self(self, share_id: str):
        share_id = share_id.replace('https://mypikpak.com/s/', "")
        """
        保存分文件到自己的账号
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/share"
        params = {
            'share_id': share_id,
            'pass_code': '',
            'page_token': '',
            'pass_code_token': '',
            'thumbnail_size': 'SIZE_LARGE',
            'limit': '100',
        }

        json_data = self.get(
            url, params=params)
        logger.debug(f"drive/v1/share:{json_data}")

        url = f"https://api-drive.mypikpak.com/drive/v1/share/restore"
        payload = {
            "folder_type": "",
            "share_id": share_id,
            "pass_code_token": json_data.get('pass_code_token'),
            "file_ids": [],
            "ancestor_ids": [],
            "params": {
                "trace_file_ids": "*",
            },
        }

        json_data = self.post(
            url, json=payload)
        logger.info(f"保存分享文件{json_data}")
        return json_data

    # #######################文件操作 这里复制pikpakapi的内容###########
    # 如果 继承方式实现 需要重新写sync token哪些也不好公用 就直接复制关键请求就好了

    def create_folder(self, name: str = "新建文件夹", parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        name: str - 文件夹名称
        parent_id: str - 父文件夹id, 默认创建到根目录

        创建文件夹
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/files"
        data = {
            "kind": "drive#folder",
            "name": name,
            "parent_id": parent_id,
        }
        result = self.post(url, json=data)
        return result

    def delete_to_trash(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        将文件夹、文件移动到回收站
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/files:batchTrash"
        data = {
            "ids": ids,
        }
        result = self.post(url, json=data)
        return result

    def untrash(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        将文件夹、文件移出回收站
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/files:batchUntrash"
        data = {
            "ids": ids,
        }
        result = self.post(url, json=data)
        return result

    def delete_forever(self, ids: List[str]) -> Dict[str, Any]:
        """
        ids: List[str] - 文件夹、文件id列表

        永远删除文件夹、文件, 慎用
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/files:batchDelete"
        data = {
            "ids": ids,
        }
        result = self.post(url, json=data)
        return result

    def offline_download(self, file_url: str, parent_id: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        file_url: str - 文件链接
        parent_id: str - 父文件夹id, 不传默认存储到 My Pack
        name: str - 文件名, 不传默认为文件链接的文件名

        离线下载磁力链
        """
        download_url = f"https://api-drive.mypikpak.com/drive/v1/files"
        download_data = {
            "kind": "drive#file",
            "name": name,
            "upload_type": "UPLOAD_TYPE_URL",
            "url": {"url": file_url},
            "folder_type": "DOWNLOAD" if not parent_id else "",
            "parent_id": parent_id,
        }
        result = self.post(download_url, json=download_data)
        return result

    def offline_list(self, size: int = 10000, next_page_token: Optional[str] = None, phase: Optional[List[str]] = None,) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        next_page_token: str - 下一页的page token
        phase: List[str] - Offline download task status, default is ["PHASE_TYPE_RUNNING", "PHASE_TYPE_ERROR"]
            supported values: PHASE_TYPE_RUNNING, PHASE_TYPE_ERROR, PHASE_TYPE_COMPLETE, PHASE_TYPE_PENDING

        获取离线下载列表
        """
        if phase is None:
            phase = ["PHASE_TYPE_RUNNING", "PHASE_TYPE_ERROR"]
        list_url = f"https://api-drive.mypikpak.com/drive/v1/tasks"
        list_data = {
            "type": "offline",
            "thumbnail_size": "SIZE_SMALL",
            "limit": size,
            "page_token": next_page_token,
            "filters": json.dumps({"phase": {"in": ",".join(phase)}}),
            "with": "reference_resource",
        }
        result = self.get(list_url, params=list_data)
        return result

    def offline_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        file_id: str - 离线下载文件id

        离线下载文件信息
        """
        url = f"https://api-drive.mypikpak.com/drive/v1/files/{file_id}"
        result = self.get(url, params={"thumbnail_size": "SIZE_LARGE"})
        return result

    def file_list(
        self,
        size: int = 100,
        parent_id: Optional[str] = None,
        next_page_token: Optional[str] = None,
        additional_filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        parent_id: str - 父文件夹id, 默认列出根目录
        next_page_token: str - 下一页的page token
        additional_filters: Dict[str, Any] - 额外的过滤条件

        获取文件列表，可以获得文件下载链接
        """
        default_filters = {
            "trashed": {"eq": False},
            "phase": {"eq": "PHASE_TYPE_COMPLETE"},
        }
        if additional_filters:
            default_filters.update(additional_filters)
        list_url = f"https://api-drive.mypikpak.com/drive/v1/files"
        list_data = {
            "parent_id": parent_id,
            "thumbnail_size": "SIZE_MEDIUM",
            "limit": size,
            "with_audit": "true",
            "page_token": next_page_token,
            "filters": json.dumps(default_filters),
        }
        result = self.get(list_url, params=list_data)
        return result

    def events(
        self, size: int = 100, next_page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        size: int - 每次请求的数量
        next_page_token: str - 下一页的page token

        获取最近添加事件列表
        """
        list_url = f"https://api-drive.mypikpak.com/drive/v1/events"
        list_data = {
            "thumbnail_size": "SIZE_MEDIUM",
            "limit": size,
            "next_page_token": next_page_token,
        }
        result = self.get(list_url, params=list_data)
        return result

    def offline_task_retry(self, task_id: str) -> Dict[str, Any]:
        """
        task_id: str - 离线下载任务id

        重试离线下载任务
        """
        list_url = f"https://api-drive.mypikpak.com/drive/v1/task"
        list_data = {
            "type": "offline",
            "create_type": "RETRY",
            "id": task_id,
        }
        try:
            result = self.post(list_url, json=list_data)
            return result
        except Exception as e:
            raise Exception(f"重试离线下载任务失败: {task_id}. {e}")

    _path_id_cache = {}

    def path_to_id(self, path: str, create: bool = False) -> List[Dict[str, str]]:
        """
        path: str - 路径
        create: bool - 是否创建不存在的文件夹

        将形如 /path/a/b 的路径转换为 文件夹的id
        """
        if not path or len(path) <= 0:
            return []
        paths = path.split("/")
        paths = [p.strip() for p in paths if len(p) > 0]
        # 构造不同级别的path表达式，尝试找到距离目标最近的那一层
        multi_level_paths = [
            "/" + "/".join(paths[: i + 1]) for i in range(len(paths))]
        path_ids = [
            self._path_id_cache[p]
            for p in multi_level_paths
            if p in self._path_id_cache
        ]
        # 判断缓存命中情况
        hit_cnt = len(path_ids)
        if hit_cnt == len(paths):
            return path_ids
        elif hit_cnt == 0:
            count = 0
            parent_id = None
        else:
            count = hit_cnt
            parent_id = path_ids[-1]["id"]

        next_page_token = None
        while count < len(paths):
            current_parent_path = "/" + "/".join(paths[:count])
            data = self.file_list(
                parent_id=parent_id, next_page_token=next_page_token
            )
            record_of_target_path = None
            for f in data.get("files", []):
                current_path = "/" + "/".join(paths[:count] + [f.get("name")])
                file_type = (
                    "folder" if f.get("kind", "").find(
                        "folder") != -1 else "file"
                )
                record = {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "file_type": file_type,
                }
                self._path_id_cache[current_path] = record
                if f.get("name") == paths[count]:
                    record_of_target_path = record
                    # 不break: 剩下的文件也同样缓存起来
            if record_of_target_path is not None:
                path_ids.append(record_of_target_path)
                count += 1
                parent_id = record_of_target_path["id"]
            elif data.get("next_page_token") and (
                not next_page_token or next_page_token != data.get(
                    "next_page_token")
            ):
                next_page_token = data.get("next_page_token")
            elif create:
                data = self.create_folder(
                    name=paths[count], parent_id=parent_id)
                id = data.get("file").get("id")
                record = {
                    "id": id,
                    "name": paths[count],
                    "file_type": "folder",
                }
                path_ids.append(record)
                current_path = "/" + "/".join(paths[: count + 1])
                self._path_id_cache[current_path] = record
                count += 1
                parent_id = id
            else:
                break
        return path_ids

    def file_batch_move(
        self,
        ids: List[str],
        to_parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        ids: List[str] - 文件id列表
        to_parent_id: str - 移动到的文件夹id, 默认为根目录

        批量移动文件
        """
        to = (
            {
                "parent_id": to_parent_id,
            }
            if to_parent_id
            else {}
        )
        result = self.post(
            url=f"https://api-drive.mypikpak.com/drive/v1/files:batchMove",
            json={
                "ids": ids,
                "to": to,
            },
        )
        return result

    def file_batch_copy(
        self,
        ids: List[str],
        to_parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        ids: List[str] - 文件id列表
        to_parent_id: str - 复制到的文件夹id, 默认为根目录

        批量复制文件
        """
        to = (
            {
                "parent_id": to_parent_id,
            }
            if to_parent_id
            else {}
        )
        result = self.post(
            url=f"https://api-drive.mypikpak.com/drive/v1/files:batchCopy",
            json={
                "ids": ids,
                "to": to,
            },
        )
        return result

    def file_move_or_copy_by_path(
        self,
        from_path: List[str],
        to_path: str,
        move: bool = False,
        create: bool = False,
    ) -> Dict[str, Any]:
        """
        from_path: List[str] - 要移动或复制的文件路径列表
        to_path: str - 移动或复制到的路径
        is_move: bool - 是否移动, 默认为复制
        create: bool - 是否创建不存在的文件夹

        根据路径移动或复制文件
        """
        from_ids: List[str] = []
        for path in from_path:
            if path_ids := self.path_to_id(path):
                if id := path_ids[-1].get("id"):
                    from_ids.append(id)
        if not from_ids:
            raise Exception("要移动的文件不存在")
        to_path_ids = self.path_to_id(to_path, create=create)
        if to_path_ids:
            to_parent_id = to_path_ids[-1].get("id")
        else:
            to_parent_id = None
        if move:
            result = self.file_batch_move(
                ids=from_ids, to_parent_id=to_parent_id)
        else:
            result = self.file_batch_copy(
                ids=from_ids, to_parent_id=to_parent_id)
        return result

    def get_download_url(self, file_id: str) -> Dict[str, Any]:
        """
        id: str - 文件id

        Returns the file details data.
        1. Use `medias[0][link][url]` for streaming with high speed in streaming services or tools.
        2. Use `web_content_link` to download the file
        """
        result = self.get(
            url=f"https://api-drive.mypikpak.com/drive/v1/files/{file_id}?",
        )
        return result

    def file_batch_share(
        self,
        ids: List[str],
        need_password: Optional[bool] = False,
        expiration_days: Optional[int] = -1,
    ) -> Dict[str, Any]:
        """
        ids: List[str] - 文件id列表
        need_password: Optional[bool] - 是否需要分享密码
        expiration_days: Optional[int] - 分享天数

        批量分享文件，并生成分享链接
        返回数据结构：
        {
            "share_id": "xxx", //分享ID
            "share_url": "https://mypikpak.com/s/xxx", // 分享链接
            "pass_code": "53fe", // 分享密码
            "share_text": "https://mypikpak.com/s/xxx",
            "share_list": []
        }
        """
        data = {
            "file_ids": ids,
            "share_to": "encryptedlink" if need_password else "publiclink",
            "expiration_days": expiration_days,
            "pass_code_option": "REQUIRED" if need_password else "NOT_REQUIRED",
        }
        result = self.post(
            url=f"https://api-drive.mypikpak.com/drive/v1/share",
            json=data,
        )
        return result
    # 文件操作再次结束


if __name__ == "__main__":
    email = ""
    password = ""
    pikpak_ = ChromePikpak(email, password)
    pikpak_.login()
    SukebeiEnyo合集一 = pikpak_.path_to_id(
        "/Pack From Shared/test")[-1]
    next_page_token = None
    move_path = pikpak_.path_to_id(
        "/Pack From Shared/", True)[-1]
    while True:
        file_list = pikpak_.file_list(10, SukebeiEnyo合集一.get(
            "id"), next_page_token=next_page_token)
        next_page_token = file_list.get('next_page_token')
        for max_folder_50G in file_list.get("files"):
            if 'max_folder_50G' in max_folder_50G.get("name"):
                ids = []
                for file in pikpak_.file_list(
                        500, max_folder_50G.get("id")).get('files'):
                    ids.append(file.get("id"))
                if len(ids) > 0:
                    pikpak_.file_batch_move(ids, move_path.get("id"))
                time.sleep(2)
                if len(pikpak_.file_list(
                        2, max_folder_50G.get("id")).get('files')) <= 0:
                    pikpak_.delete_to_trash([max_folder_50G.get("id")])
            else:
                pikpak_.file_batch_move(
                    [max_folder_50G.get('id')], move_path.get("id"))
        if len(file_list.get('files')) <= 0:
            break
        time.sleep(2)
