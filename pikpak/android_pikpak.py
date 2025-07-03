import logging
import os
import random
from urllib.parse import urlparse
from pikpak.captcha_js2py import get_d, img_jj
from pikpak.chrome_pikpak import ChromePikpak, DEF_AUTHORIZATION
from proxy_ip import pop_prxy_pikpak
import uuid
import time

from config.config import get_captcha_callback
from typing import Any, Dict, List, Optional

from tools import set_def_callback

# logger = logging.getLogger(os.path.splitext(os.path.split(__file__)[1])[0])

logger = logging.getLogger("Android_pikpak")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

download_test = "magnet:?xt=urn:btih:C875E08EAC834DD82D34D2C385BBAB598415C98A"

PHONE_LIST= [
    {
        "name":"Lge",
        "model":"Lgm-v300k",
        "ANDROID_SDK":"25",
        "ANDROID_VERSION":"7.1.2",
    },
    {
        "name":"OnePlus",
        "model":"HD1910",
        "ANDROID_SDK":"30",
        "ANDROID_VERSION":"11.0.0",
    },
    {
        "name":"OnePlus",
        "model":"HD1913",
        "ANDROID_SDK":"31",
        "ANDROID_VERSION":"12.0.0",
    },
    {
        "name":"OnePlus",
        "model":"HD1911",
        "ANDROID_SDK":"27",
        "ANDROID_VERSION":"8.1.0",
    },
    {
        "name":"OnePlus",
        "model":"GM1915",
        "ANDROID_SDK":"28",
        "ANDROID_VERSION":"9.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2447",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2451",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2653",
        "ANDROID_SDK":"31",
        "ANDROID_VERSION":"12.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2655",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"OnePlus",
        "model":"PKX110",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2653",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"OnePlus",
        "model":"CPH2609",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"vivo",
        "model":"V1937",
        "ANDROID_SDK":"28",
        "ANDROID_VERSION":"9.0.0",
    },
    {
        "name":"vivo",
        "model":"V2126",
        "ANDROID_SDK":"29",
        "ANDROID_VERSION":"10.0.0",
    },
    {
        "name":"vivo",
        "model":"V2202",
        "ANDROID_SDK":"28",
        "ANDROID_VERSION":"9.0.0",
    },
    {
        "name":"vivo",
        "model":"V2158",
        "ANDROID_SDK":"28",
        "ANDROID_VERSION":"9.0.0",
    },
    {
        "name":"vivo",
        "model":"V2231",
        "ANDROID_SDK":"31",
        "ANDROID_VERSION":"12.0.0",
    },
    {
        "name":"vivo",
        "model":"V2318",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"vivo",
        "model":"V2339",
        "ANDROID_SDK":"31",
        "ANDROID_VERSION":"12.0.0",
    },
    {
        "name":"vivo",
        "model":"V2314",
        "ANDROID_SDK":"28",
        "ANDROID_VERSION":"9.0.0",
    },
    {
        "name":"vivo",
        "model":"V2349",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"vivo",
        "model":"V2348",
        "ANDROID_SDK":"31",
        "ANDROID_VERSION":"12.0.0",
    },
    {
        "name":"vivo",
        "model":"V1937",
        "ANDROID_SDK":"27",
        "ANDROID_VERSION":"8.1.0",
    },
    {
        "name":"Xiaomi",
        "model":"2206123SC",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2206122SC",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2203121C",
        "ANDROID_SDK":"33",
        "ANDROID_VERSION":"13.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"22071212AG",
        "ANDROID_SDK":"34",
        "ANDROID_VERSION":"14.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"22081212UG",
        "ANDROID_SDK":"34",
        "ANDROID_VERSION":"14.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2211133G",
        "ANDROID_SDK":"35",
        "ANDROID_VERSION":"15.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2210132C",
        "ANDROID_SDK":"34",
        "ANDROID_VERSION":"14.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2210129SG",
        "ANDROID_SDK":"34",
        "ANDROID_VERSION":"14.0.0",
    },
    {
        "name":"Xiaomi",
        "model":"2306EPN60G",
        "ANDROID_SDK":"34",
        "ANDROID_VERSION":"14.0.0",
    },
]

class AndroidPikPak(ChromePikpak):
    country = "US"

    language = "zh-TW"

    CLIENT_VERSION = "1.51.2"
    # 手机型号
    phone_model = "Lgm-v300k"
    # 手机品牌
    phone_name = "Lge"

    CLIENT_ID = "YNxT9w7GMdWvEOKa"

    CLIENT_SECRET = "dbw2OtmVEeuUvIptb1Coyg"

    SDK_VERSION = "2.0.6.206003"

    VERSION_CODE = "10241"

    INSTALL_FROM = "other"

    ANDROID_VERSION = "7.1.2"
    ANDROID_SDK = "25"

    PACKAGE_NAME = "com.pikcloud.pikpak"

    device_id2 = str(uuid.uuid4()).replace("-", "")
    # 仿制captcha_sign

    cache_json_file = os.path.abspath(__file__)[:-3] + "user" + ".json"

    android_device_index = 0

    def __init__(
        self,
        mail: str,
        pd: str,
    ):
        super().__init__(mail, pd)
        self.android_device_index = random.randint(0, len(PHONE_LIST) - 1)
        self.__update_android_device_info()

    def __update_android_device_info(self):
        self.phone_name = PHONE_LIST[self.android_device_index].get("name")
        self.phone_model = PHONE_LIST[self.android_device_index].get("model")
        self.ANDROID_VERSION = PHONE_LIST[self.android_device_index].get(
            "ANDROID_VERSION"
        )
        self.ANDROID_SDK = PHONE_LIST[self.android_device_index].get("ANDROID_SDK")

    def save_json(self):
        json_data = super().save_json()
        json_data[self.mail].update({
            "android_device_index": self.android_device_index,
        })
        return json_data

    # 应用存入的json数据
    def apply_json(self, json_data: dict):
        super().apply_json(json_data)
        data = json_data.get(self.mail)
        if data:
            self.android_device_index = data.get("android_device_index", 0)
        self.__update_android_device_info()

    def headers(self, url: str):
        # 解析 URL
        parsed_url = urlparse(url)

        # 获取主机名
        hostname = parsed_url.hostname
        # 分割主机名并提取二级域名
        if hostname:
            parts = hostname.split(".")
            if len(parts) >= 3:  # 确保有足够的部分
                second_level_domain = parts[-3]  # 倒数第三个部分
                # logger.debug(f'二级域名: {second_level_domain}')

        if "v1/shield/captcha/init" in url:
            time_str = self.captcha_time
        else:
            time_str = str(int(round(time.time() * 1000)))
        header_config = {
            "install-from": self.INSTALL_FROM,
            "language-app": self.language,
            "x-user-id": self.user_id,
            "x-device-id": self.device_id,
            "product-flavor-name": "cha",
            "country": self.country,
            "build-manufacturer": self.phone_name.upper(),
            "product_flavor_name": "cha",
            "sdk-int": self.ANDROID_SDK,
            "x-client-version": self.CLIENT_VERSION,
            "phone-model": self.phone_model,
            "language-system": self.language,
            "version-code": self.VERSION_CODE,
            "version-name": self.CLIENT_VERSION,
            "channel-id": "official",
            "mobile-type": "android",
            "build-version-release": self.ANDROID_VERSION,
            "system-version": self.ANDROID_SDK,
            "x-client-id": self.CLIENT_ID,
            "build-sdk-int": self.ANDROID_SDK,
            "app-type": "android",
            "platform-version": self.ANDROID_VERSION,
            "x-system-language": self.language,
            "content-type": "application/json; charset=utf-8",
            # "content-length": "283",
            "accept-encoding": "gzip",
            "user-agent": f"ANDROID-{self.PACKAGE_NAME}/{self.CLIENT_VERSION} accessmode/ devicename/{self.phone_model} appname/android-{self.PACKAGE_NAME} appid/ action_type/ clientid/{self.CLIENT_ID} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/{self.phone_model} networktype/WIFI accesstype/ sessionid/ osversion/{self.ANDROID_VERSION} datetime/{time_str} protocolversion/200 sdkversion/{self.SDK_VERSION} clientversion/{self.CLIENT_VERSION} providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/{self.user_id}",
            "x-captcha-token": self.captcha_token or "",
            "authorization": self.authorization,
        }

        header_user = {
            "accept-encoding": "gzip",
            "accept-language": self.language,
            "content-type": "application/json; charset=utf-8",
            "user-agent": f"ANDROID-{self.PACKAGE_NAME}/{self.CLIENT_VERSION} accessmode/ devicename/{self.phone_model} appname/android-{self.PACKAGE_NAME} appid/ action_type/ clientid/{self.CLIENT_ID} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/{self.phone_model} networktype/WIFI accesstype/ sessionid/ osversion/{self.ANDROID_VERSION} datetime/{time_str} protocolversion/200 sdkversion/{self.SDK_VERSION} clientversion/{self.CLIENT_VERSION} providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/{self.user_id}",
            "x-captcha-token": self.captcha_token or "",
            "x-client-id": self.CLIENT_ID,
            "authorization": self.authorization,
            "x-device-id": self.device_id,
        }

        headers = {
            "config": header_config,
            "api-drive": header_config,
            "user": header_user,
        }
        return headers.get(second_level_domain)

    # 设置邀请

    def report(self):
        url = "https://api-drive.mypikpak.com/operating/v1/report"
        json = {
            "data": {
                "version": self.CLIENT_VERSION,
                "versioncode": self.VERSION_CODE,
                "install_from": "other",
                "device_id": self.device_id,
                "language_system": self.language,
                "language_app": self.language,
                "country": self.country,
                "channel_id": "official",
                "product_flavor_name": "cha",
                "user_id": self.user_id,
            },
            "client": "android",
            "id": "m20230322001",
            "attr": "REPORT_ATTR_TITLE",
        }

        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\nreport:\n{json_data}")

    def authorize(self):
        url = "https://user.mypikpak.com/v1/user/authorize"
        json = {
            "client_id": "YUMx5nI8ZU8Ap8pm",
            "response_type": "code",
            "redirect_uri": "https://mypikpak.com/drive/account",
            "scope": "user+pan",
            "state": "ignored",
        }
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\nreport:\n{json_data}")

    def introspect(self):
        url = "https://user.mypikpak.com/v1/auth/token/introspect"
        params = {
            "token": self.authorization[len("Bearer "):],
        }
        json_data = self.get(url, params=params)
        logger.debug(f"{self.mail}----\n introspect:\n{json_data}")

    def revoke(self):
        pass
        url ="https://user.mypikpak.com/v1/auth/revoke"
        json = {
            "token": self.authorization[len("Bearer ") :],
        }
        handler = {
            "content-length": "2",
            "x-platform-version": "3",
            "x-provider-name": "NONE",
            "x-protocol-version": "301",
            "x-device-sign": f"wdi10.{self.device_id}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "accept-language": self.language,
            "user-agent": f"Mozilla/5.0 (Linux; Android 7.1.2; {self.phone_model} Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36PikPak {self.CLIENT_VERSION}",
            "x-client-version": "1.0.0",
            "content-type": "application/json",
            "x-os-version": "Linux%20i686",
            "x-client-id": "YUMx5nI8ZU8Ap8pm",
            "x-device-model": "chrome%2F92.0.4515.131",
            "x-net-work-type": "NONE",
            "x-sdk-version": "8.0.3",
            "x-device-id": self.device_id,
            "x-device-name": "Mobile-Chrome",
            "accept": "*/*",
            "origin": "https://mypikpak.com",
            "x-requested-with": "com.pikcloud.pikpak",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mypikpak.com/",
            "accept-encoding": "gzip, deflate",
        }
        json_data = self.post(url, json=json, handler=handler)
        logger.debug(f"{self.mail}----\nrevoke:\n{json_data}")

    def auth_token(self):
        url = "https://user.mypikpak.com/v1/auth/token"
        json = {
            "code": self.authorization,
            "grant_type": "authorization_code",
            "client_id": self.CLIENT_ID,
        }
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\nauth_token:\n{json_data}")

    def set_activation_code(self, activation_code):
        url = f"https://api-drive.mypikpak.com/vip/v1/order/activation-code"
        payload = {
            "activation_code": str(activation_code),
            "page": "invite",
        }
        json_data = self.post(url, json=payload)
        error = json_data.get("error")
        if not error or error == "":
            self.isInvise = True
        else:
            self.inviseError = json_data.get("error")
            raise Exception(self.inviseError)
        logger.debug(f"{self.mail}----\n填写邀请结果返回:\n{json_data}")

    # 注册
    def register(self):
        # self.captcha("POST:/v1/auth/verification")
        url = "https://user.mypikpak.com/v1/auth/verification"
        json_data = {
            "email": self.mail,
            "target": "ANY",
            "locale": self.language,
            "usage": "REGISTER",
            "client_id": self.CLIENT_ID,
        }
        params = {
            "client_id": self.CLIENT_ID,
        }
        json_data = self.post(url, json=json_data, params=params)
        logger.debug(f"{self.mail}----\nverification 数据{json_data}")
        verification_id = json_data.get("verification_id")
        if verification_id:
            pass
        else:
            raise Exception(json_data.get("error"))
        code = self.handler.run_get_maincode(self.mail)
        url = f"https://user.mypikpak.com/v1/auth/verification/verify"
        payload = {
            "client_id": self.CLIENT_ID,
            "verification_id": verification_id,
            "verification_code": code,
        }
        json_data = self.post(url, json=payload, params=params)
        logger.debug(f"{self.mail}----\nverification/verify 数据{json_data}")
        verification_token = json_data.get("verification_token")
        if verification_token and verification_token != "":
            pass
        else:
            raise Exception(json_data.get("error"))

        url = f"https://user.mypikpak.com/v1/auth/signup"
        payload = {
            "captcha_token": self.captcha_token,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "email": self.mail,
            "name": self.mail.split("@")[0],
            "password": self.pd,
            "verification_token": verification_token,
        }
        json_data = self.post(url, json=payload, params=params)
        logger.debug(f"{self.mail}----\nsignup 数据{json_data}")
        if json_data.get("error"):
            raise Exception(json_data.get("error"))
        self.user_id = json_data.get("sub")
        self.authorization = (
            f"{json_data.get('token_type')} {json_data.get('access_token')}"
        )
        self.refresh_token = json_data.get("refresh_token")
        self.create_self_time = time.time()
        self.save_self()

    def login(self, redconf=True):
        if redconf:
            self.read_self()
        if self.authorization and self.authorization != "" and self.authorization != DEF_AUTHORIZATION:
            logger.debug("已经登陆了")
            return
        if self.refresh_token and self.refresh_token != "":
            self.refresh_access_token()
        url = f"https://user.mypikpak.com/v1/auth/signin"
        body = {
            "username": self.mail,
            "password": self.pd,
            "captcha_token": self.captcha_token,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
        }
        query = {
            "client_id": self.CLIENT_ID,
        }
        json_data = self.post(url, json=body, params=query)
        if not json_data.get('error'):
            logger.debug(f"{self.mail}----\n登陆成功{json_data}")
            self.user_id = json_data.get("sub")
            self.authorization = f"{json_data.get('token_type')} {json_data.get('access_token')}"
            self.refresh_token = json_data.get('refresh_token')
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
        url = "https://user.mypikpak.com/v1/user/me"
        json_data = self.get(url)
        logger.debug(f"{self.mail}----\n自己的数据{json_data}")

    def configs(self):
        url = "https://config.mypikpak.com/config/v1/globalConfig"
        json = {
            "data": {
                "version": self.CLIENT_VERSION,
                "versioncode": self.VERSION_CODE,
                "install_from": self.INSTALL_FROM,
                "device_id": self.device_id,
                "language_system": self.language,
                "language_app": self.language,
                "country": self.country,
                "channel_id": "official",
                "product_flavor_name": "cha",
                "user_id": self.user_id,
            },
            "client": "android",
        }
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\n globalConfig 返回值:{json_data}")

        url = "https://api-drive.mypikpak.com/operating/v1/content"
        json_data = self.post(url)
        logger.debug(f"{self.mail}----\n operating/v1/content 返回值:{json_data}")

        urls = [
            "https://access.mypikpak.com/access_controller/v1/area_accessible",
            "https://access.mypikpak.com/access_controller/v1/area_accessible",
            "https://access.mypikpak.com/access_controller/v1/area_accessible",
            "https://access.mypikpak.com/drive/v1/privilege/area_shareable",
            "https://access.mypikpak.com/drive/v1/privilege/area_shareable",
            "https://api-drive.mypikpak.com/user/v1/settings?items=enablePrivacyMode",
            "https://api-drive.mypikpak.com/user/v1/settings?items=enablePrivacyMode",
            "https://api-drive.mypikpak.com/vip/v1/allSubscriptionStatus",
            "https://api-drive.mypikpak.com/vip/v1/allSubscriptionStatus",
            "https://api-drive.mypikpak.com/vip/v1/activity/invite/permission",
            "https://api-drive.mypikpak.com/vip/v1/activity/invite/permission",
            "https://api-drive.mypikpak.com/vip/v1/activity/invite/permission",
            "https://api-drive.mypikpak.com/vip/v1/activity/invite/permission/review",
            "https://api-drive.mypikpak.com/vip/v1/activity/invite/permission/review",
            "https://api-drive.mypikpak.com/vip/v1/pay/settings",
            "https://api-drive.mypikpak.com/vip/v1/pay/settings",
            "https://api-drive.mypikpak.com/vip/v1/pay/settings",
            "https://api-drive.mypikpak.com/drive/v1/privilege/area_connectivity",
            "https://api-drive.mypikpak.com/drive/v1/privilege/area_connectivity",
            "https://api-drive.mypikpak.com/drive/v1/privilege/area_connectivity",
        ]
        random.shuffle(urls)
        for url in urls:
            json_data = self.get(url)
            logger.debug(f"{self.mail}----\n url:{url} \n 返回值:{json_data}")

        callbacks = [
            self.connectivity_probe_results,
            self.urlsOnInstall,
            self.checkClientVersion,
            self.report,
            self.authorize,
            self.introspect,
            self.me,
            self.vip_info,
            self.logReportSwitch,

            self.connectivity_probe_results,
            self.urlsOnInstall,
            self.checkClientVersion,
            self.report,
            self.authorize,
            self.introspect,
            self.me,
            self.vip_info,

            self.connectivity_probe_results,
            self.urlsOnInstall,
            self.checkClientVersion,
            self.report,
            self.authorize,
            self.introspect,
            self.me,
            self.vip_info,
        ]
        random.shuffle(callbacks)
        for callback in callbacks:
            callback()

    def connectivity_probe_results(self):
        url = "https://api-drive.mypikpak.com/connectivity_probe/v1/targets"
        json_data = self.get(url)
        logger.debug(f"{self.mail}----\nconnectivity_probe_targets:get::::{json_data}")

        succeed = []
        fail= []
        detail=[]

        for data in json_data.get("targets"):
            succeed.append(data.get("id"))
            detail.append({
                "id":data.get("id"),
                "kind":data.get("data"),
                "error":"",
                "time_ms":random.randint(300,999),
                "domain":data.get("link"),
            })
        json = {
            "succeed" : succeed,
            "fail":fail,
            "detail":detail,
        }
        url = "https://api-drive.mypikpak.com/connectivity_probe/v1/results"
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\nconnectivity_probe_results:{json_data}")

    def urlsOnInstall(self):
        url = "https://config.mypikpak.com/config/v1/urlsOnInstall"
        json = {
            "data": {
                "sdk_int": self.ANDROID_SDK,
                "uuid": self.device_id,
                "userType": "1",
                "userid": self.user_id,
                "userSub": "regional",
                "language_system": self.language,
                "language_app": self.language,
                "build_version_release": self.ANDROID_VERSION,
                "phoneModel": self.phone_model,
                "build_manufacturer": self.phone_name.upper(),
                "build_sdk_int": self.ANDROID_SDK,
                "channel": "official",
                "versionCode": self.VERSION_CODE,
                "versionName": self.CLIENT_VERSION,
                "country": self.country,
                "install_from": "other",
            }
        }
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\nurlsOnInstall:{json_data}")

    def invite(self):
        url = 'https://api-drive.mypikpak.com/vip/v1/activity/invite'
        json = {
            "data": {
                "sdk_int": self.ANDROID_SDK,
                "uuid": self.device_id,
                "userType": "1",
                "userid": self.user_id,
                "userSub": "",
                "product_flavor_name": "cha",
                "language_system": self.language,
                "language_app": self.language,
                "build_version_release": self.ANDROID_VERSION,
                "phoneModel": self.phone_model,
                "build_manufacturer": self.phone_name.upper(),
                "build_sdk_int": self.ANDROID_SDK,
                "channel": "official",
                "versionCode": self.VERSION_CODE,
                "versionName": self.CLIENT_VERSION,
                "installFrom": self.INSTALL_FROM,
                "country": self.country,
            },
            "apk_extra": {"channel": "official"},
        }

        json_data = self.post(url,json=json)
        logger.debug(f"{self.mail}----\ninvite:{json_data}")

    def task_reference_resource(self):
        url = 'https://api-drive.mypikpak.com/drive/v1/tasks'
        params = {
            "type": "offline",
            "page_token": "",
            "thumbnail_size": "SIZE_LARGE",
            "filters": {},
            "with": "reference_resource",
            "with": "file_ids",
            "limit": 500,
        }
        json_data = self.get(url, params=params)
        logger.debug(f"{self.mail}----\ntask_reference_resource:{json_data}")

    def checkClientVersion(self):
        url = "https://config.mypikpak.com/config/v1/checkClientVersion"
        json = {
            "data": {
                "sdk_int": self.ANDROID_SDK,
                "uuid": self.device_id,
                "userType": "1",
                "userid": self.user_id,
                "userSub": "regional",
                "language_system": self.language,
                "build_version_release": self.ANDROID_VERSION,
                "phoneModel": self.phone_model,
                "build_manufacturer": self.phone_name,
                "build_sdk_int": self.ANDROID_SDK,
                "channel": "official",
                "versionCode": f"{self.VERSION_CODE}",
                "versionName": self.CLIENT_VERSION,
                "country": self.country,
                "install_from": self.INSTALL_FROM,
                "language": self.language,
            },
            "client": "android",
        }
        json_data = self.post(url, json=json)
        logger.debug(f"{self.mail}----\ncheckClientVersion:{json_data}")

    def lbsInfo(self):
        pass

    def user_settings_bookmark(self):
        pass

    def test_config_v1_drive(self):
        pass

    def about(self):
        url = 'https://api-drive.mypikpak.com/drive/v1/about'
        json_data = self.get(url)

        logger.debug(f"{self.mail}----\nabout:{json_data}")

    def refresh_access_token(self):
        """
        Refresh access token
        """
        if not self.refresh_token or self.refresh_token == '':
            logger.debug("refresh_token没有 直接走登陆")
            self.login()
            return
        url = f"https://user.mypikpak.com/v1/auth/token"
        json = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        query = {
            "client_id": self.CLIENT_ID,
        }
        time_str = str(int(round(time.time() * 1000)))
        headers = {
            "user-agent": f"ANDROID-com.pikcloud.pikpak/{self.CLIENT_VERSION} accessmode/ devicename/{self.phone_name}_{self.phone_model} appname/android-{self.PACKAGE_NAME} appid/ action_type/ clientid/{self.CLIENT_ID} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/{self.phone_model} networktype/WIFI accesstype/ sessionid/ osversion/{self.ANDROID_VERSION} datetime/{time_str} protocolversion/200 sdkversion/{self.SDK_VERSION} clientversion/{self.CLIENT_VERSION} providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/{self.user_id}",
            "x-device-id": self.device_id,
            "accept-language": self.language,
            "content-type": "application/json; charset=utf-8",
            # "content-length": "184",
            # "accept-encoding": "gzip",
        }
        json_data = self.post(url, headers=headers, json=json, params=query)
        self.authorization = f"{json_data.get('token_type')} {json_data.get('access_token')}"
        self.refresh_token = json_data["refresh_token"]
        self.user_id = json_data["sub"]
        self.save_self()

    def logReportSwitch(self):
        url = "https://config.mypikpak.com/config/v1/logReportSwitch"
        json = {
            "data": {
                "sdk_int": self.ANDROID_SDK,
                "uuid": self.device_id,
                "userType": "1",
                "userid": self.user_id,
                "userSub": "",
                "language_system": self.language,
                "build_version_release": self.ANDROID_VERSION,
                "phoneModel": self.phone_model,
                "build_manufacturer": self.phone_name,
                "build_sdk_int": self.ANDROID_SDK,
                "channel": "official",
                "versionCode": self.VERSION_CODE,
                "versionName": self.CLIENT_VERSION,
                "country": self.country,
                "language": self.language,
            }
        }
        json_data = self.post(url,json=json)
        logger.debug(f"{self.mail}----\n logReportSwitch:{json_data}")


    # def run_test(self):
    #     """
    #     随机运行 模拟人为操作
    #     """
    #     self.login()
    #     self.me()
    #     self.configs()
    #     self.invite()
    #     self.vip_info()
    #     self.task_reference_resource()
    #     self.file_list(parent_id='*',size=500,)
    #     self.checkClientVersion()
    #     self.about()

    def installations(self):
        url = "https://firebaseinstallations.googleapis.com/v1/projects/cloud-dev-team-314113/installations"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Content-Encoding": "gzip",
            "Cache-Control": "no-cache",
            "X-Android-Package": "com.pikcloud.pikpak",
            "x-firebase-client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
            "X-Android-Cert": "D1AC8FFE217B5E0F57F3A3CF8A5AEFBBD5F34A23",
            "x-goog-api-key": "AIzaSyBgEcsTcNqf5FCCc5IgxGETr_aF3PwKtjY",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G9880 Build/PPR1.190810.011)",
            "Host": "firebaseinstallations.googleapis.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Length": "140",
        }
        params = {
            "fid": "czC_ORUkS1e6rbC2kiOlDy",
            "appId": "1:1016306462377:android:ade1992b01065d6d5fc3b8",
            "authVersion": "FIS_v2",
            "sdkVersion": "a:17.2.0",
        }

        json_data = self.post(url, headers=headers, params=params)

        url = "https://android.apis.google.com/c2dm/register3"
        headers = {
            "content-length": "832",
            "content-type": "application/x-www-form-urlencoded",
            "authorization": "AidLogin 3959706640881192963:5090764924128071634",
            "app": "com.pikcloud.pikpak",
            "gcm_ver": "252234007",
            "app_ver": "10241",
            "user-agent": "com.google.android.gms/252234007 (Linux; U; Android 7.1.2; zh_CN; SM-G9880; Build/PPR1.190810.011; Cronet/138.0.7156.0)",
            "accept-encoding": "gzip, deflate, br",
            "priority": "u=1, i",
        }
        params = {
            "X-subtype": "745476177629",
            "X-X-subscription": "745476177629",
            "sender": "745476177629",
            "X-X-subtype": "745476177629",
            "X-app_ver": "252234007",
            "X-osv": "25",
            "X-cliv": "iid-252234000",
            "X-gmsv": "252234007",
            "X-appid": "csUjJrnSWbc",
            "X-scope": "DIRECTBOOT",
            "X-subscription": "745476177629",
            "X-app_ver_name": "25.22.34%20(040700-%7B%7Bcl%7D%7D)",
            "app": "com.google.android.gms",
            "device": "3959706640881192963",
            "app_ver": "252234007",
            "info": "wyksvArr0SURoOhBO1boBVzFy-XfdRk",
            "gcm_ver": "252234007",
            "plat": "0",
            "cert": "38918a453d07199354f8b19af05ec6562ced5788",
            "target_ver": "36",
        }


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    set_def_callback()
    # # email = "bpzaof1188@nuclene.com"
    # # password = "098poi"
    # # pikpak_ = PikPak(email, password)
    # # from proxy_ip import pingPikpak
    # # # pingPikpak("43.134.68.153:3128 http", [])
    # # # pikpak_.set_proxy("43.134.68.153:3128")
    # # run_new_test(pikpak_)
    # # pikpak_.set_activation_code(98105081)
    # # pikpak_.run_req_2invite()
    # # pikpak_.save_share("VNxHRUombIy7SWJs5Oyw-TDxo1")
    # # pikpak_.get_self_invite_code()
    # # pikpak_.get_self_vip_info()

    android_pikpak = AndroidPikPak("", "")
    android_pikpak.login()
    # android_pikpak.set_proxy()
    # android_pikpak.
    # 文件:[47BT]末路狂花钱.The.Last.Frenzy.2024.WEB-DL.2160p.10Bit.60Fps.HEVC.DDP5.1下载完成
    # j3o4wxt9@smykwb.com:注册成功 并填写邀请码：78269860
    # 密码是:BKXlWy
