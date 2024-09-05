import logging
import os
from urllib.parse import urlparse
from pikpak.PikPakAPI.pikpakapi.enums import DownloadStatus
from pikpak.captcha_js2py import get_d, img_jj
from pikpak.chrome_pikpak import ChromePikpak
from proxy_ip import pop_prxy_pikpak
import enum
import hashlib
import uuid
import time

import requests
from config.config import get_captcha_callback
from mail.mail import create_one_mail, get_new_mail_code, get_code, get_mail
from pikpak.PikPakAPI.pikpakapi import PikPakApi
from typing import Any, Dict, List, Optional

from tools import set_def_callback
# logger = logging.getLogger(os.path.splitext(os.path.split(__file__)[1])[0])

logger = logging.getLogger("pikpak")

download_test = "magnet:?xt=urn:btih:C875E08EAC834DD82D34D2C385BBAB598415C98A"


class AndroidPikPak(ChromePikpak):
    country = "US"
    language = "zh-TW"

    CLIENT_VERSION = "1.48.3"
    # 手机型号
    phone_model = "Lgm-v300k"
    # 手机品牌
    phone_name = "Lge"

    CLIENT_ID = 'YNxT9w7GMdWvEOKa'

    device_id2 = str(uuid.uuid4()).replace("-", "")
    # 仿制captcha_sign

    cache_json_file = os.path.abspath(__file__)[:-3] + "user" + ".json"

    def __get_sign(self, time_str):
        begin_str = self.CLIENT_ID + \
            f"{self.CLIENT_VERSION}com.pikcloud.pikpak" + \
            self.device_id + time_str
        salts = [
            #     {'alg': 'md5', 'salt': 'Nw9cvH5q2DqkDTJG73'},
            #     {'alg': 'md5', 'salt': 'o+N/zglOE4td/6kmjQldcaT'},
            #     {'alg': 'md5', 'salt': 'SynqV'},
            #     {'alg': 'md5', 'salt': 'rObDr4xQLmbbk3K7YLn7nsNOlLmTS9h/zQNw+OjNNC'},
            #     {'alg': 'md5', 'salt': 'SD+x7W8CNeCIepTTUeENi0cPTRkQlYZuXeMHiu8KdMWs0R'},
            #     {'alg': 'md5', 'salt': 'd5bw'},
            #     {'alg': 'md5', 'salt': 'qS2pNvzAm3nkoIhK16fKVYp2yHLGwS4M'},
            #     {'alg': 'md5', 'salt': 'WKMmTWHMFLMhZxb2Nh'},
            #     {'alg': 'md5', 'salt': 'z7aRh'},
            #     {'alg': 'md5', 'salt': 'Y5qN0kxE3O'},
            #     {'alg': 'md5', 'salt': 'rpJq4'},
            #     {'alg': 'md5', 'salt': 'Lfdm3aGbd'},
            #     {'alg': 'md5', 'salt': 'X6dfcJrGemgMFLKN85ZcIl0arX3h'},
            #     {'alg': 'md5', 'salt': 'u2b'}
            # ]
            # [
            {'alg': 'md5', 'salt': 'aDhgaSE3MsjROCmpmsWqP1sJdFJ'},
            {'alg': 'md5', 'salt': '+oaVkqdd8MJuKT+uMr2AYKcd9tdWge3XPEPR2hcePUknd'},
            {'alg': 'md5', 'salt': 'u/sd2GgT2fTytRcKzGicHodhvIltMntA3xKw2SRv7S48OdnaQIS5mn'},
            {'alg': 'md5', 'salt': '2WZiae2QuqTOxBKaaqCNHCW3olu2UImelkDzBn'},
            {'alg': 'md5', 'salt': '/vJ3upic39lgmrkX855Qx'},
            {'alg': 'md5', 'salt': 'yNc9ruCVMV7pGV7XvFeuLMOcy1'},
            {'alg': 'md5', 'salt': '4FPq8mT3JQ1jzcVxMVfwFftLQm33M7i'},
            {'alg': 'md5', 'salt': 'xozoy5e3Ea'}
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
                # logger.debug(f'二级域名: {second_level_domain}')
        t = time.time()
        header_config = {
            "install-from": "other",
            "language-app": "zh-CN",
            "x-user-id": self.user_id,
            "x-device-id": self.device_id,
            "country": "TW",
            "build-manufacturer": "LGE",
            "product_flavor_name": "cha",
            "sdk-int": "25",
            "x-client-version": self.CLIENT_VERSION,
            "phone-model": self.phone_model,
            "language-system": "zh-CN",
            "version-code": '10216',
            'version-name': self.CLIENT_VERSION,
            'channel-id': 'official',
            'mobile-type': 'android',
            'build-version-release': '7.1.2',
            'system-version': '25',
            'x-client-id': self.CLIENT_ID,
            'build-sdk-int': '25',
            'app-type': 'android',
            'platform-version': "7.1.2",
            'x-system-language': 'zh-CN',
            'content-type': 'application/json; charset=utf-8',
            'content-length': '283',
            'accept-encoding': 'gzip',
            'user-agent': f'ANDROID-com.pikcloud.pikpak/1.48.3 accessmode/ devicename/{self.phone_model} appname/android-com.pikcloud.pikpak appid/ action_type/ clientid/{self.CLIENT_ID} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/{self.phone_model} networktype/WIFI accesstype/ sessionid/ osversion/7.1.2 datetime/{int(round(t * 1000))} protocolversion/200 sdkversion/2.0.4.204101 clientversion/{self.CLIENT_VERSION} providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/{self.user_id}',
            'x-captcha-token': self.captcha_token or ''

        }

        header_user = {
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN',
            'content-type': 'application/json; charset=utf-8',
            'user-agent': f'ANDROID-com.pikcloud.pikpak/1.48.3 accessmode/ devicename/{self.phone_model} appname/android-com.pikcloud.pikpak appid/ action_type/ clientid/{self.CLIENT_ID} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/{self.phone_model} networktype/WIFI accesstype/ sessionid/ osversion/7.1.2 datetime/{int(round(t * 1000))} protocolversion/200 sdkversion/2.0.4.204101 clientversion/{self.CLIENT_VERSION} providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/{self.user_id}',
            'x-captcha-token': self.captcha_token,
            'x-client-id': self.CLIENT_ID,
            "content-length": '1042',
            'authorization': self.authorization,
        }

        headers = {
            'config': header_config,
            "api-drive": header_config,
            "user": header_user,
        }
        return headers.get(second_level_domain)


    # 设置邀请
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
        logger.debug(f"填写邀请结果返回:\n{json_data}")


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

    android_pikpak = AndroidPikPak("", '')
    android_pikpak.login()
    # android_pikpak.set_proxy()
    # android_pikpak.
    # 文件:[47BT]末路狂花钱.The.Last.Frenzy.2024.WEB-DL.2160p.10Bit.60Fps.HEVC.DDP5.1下载完成
    # j3o4wxt9@smykwb.com:注册成功 并填写邀请码：78269860
    # 密码是:BKXlWy
