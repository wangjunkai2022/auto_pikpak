import importlib
import logging

import requests

from captcha.utils import domain_get, extract_parameters, remove_parameters
from config.config import mail_api


logger = logging.getLogger("rapidapi")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

sitekey_login = "6LdwHgcqAAAAACSTxyrqqnHNY9-NdSvRD-1A1eap"
sitekey_rewardVip = "6LerFi0pAAAAAB8PSfeUmwtJx6imhQpza2dCjMmG"


class BaseRapidapi():
    api_url = ''
    key_api_params_url = ""
    key_api_params_sitekey = ''
    params = {}

    def pikpak_req(self, url: str = "", sitekey=sitekey_login):
        params_dict = extract_parameters(url)
        url = remove_parameters(url)
        solvev2e_url = self.api_url
        self.params[self.key_api_params_url] = f"{url}"
        self.params[self.key_api_params_sitekey] = f"{sitekey}"
        headers = {
            "x-rapidapi-key": mail_api,
            "x-rapidapi-host": domain_get(self.api_url),
        }
        result = requests.get(
            solvev2e_url, headers=headers, params=self.params)
        if result.status_code != 200:
            logger.debug(f"pikpak_req 失败:{result.text}")
            raise Exception("pikpak_req 报错了")
        result_json = result.json()
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
            'data': result_json.get("result")

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

    def pikpak_rewardVip(self, sitekey: str = sitekey_rewardVip):
        url = "https://user.mypikpak.com"
        solvev2e_url = self.api_url
        self.params[self.key_api_params_url] = f"{url}"
        self.params[self.key_api_params_sitekey] = f"{sitekey}"
        headers = {
            "x-rapidapi-key": mail_api,
            "x-rapidapi-host": domain_get(self.api_url),
        }
        result = requests.get(
            solvev2e_url, headers=headers, params=self.params)
        if result.status_code != 200:
            logger.error(f"captcha_rewardVip 失败:{result.text}")
            raise Exception("pikpak_rewardVip 报错了")
        logger.info(result)
        result_json = result.json()
        return result_json.get("result")


# 定义要创建的类名集合
class_names = {
    "Captcha2": "captcha.rapidapi.child.2captcha",
    "CaptchaKiller": "captcha.rapidapi.child.captcha_killer",
    'Capsolver': 'captcha.rapidapi.child.capsolver',
}


def _getInstanceClass(class_name) -> BaseRapidapi:
    module_name = class_names.get(class_name)
    if module_name:
        # 动态导入模块
        module = importlib.import_module(module_name)
        # 获取类对象
        cls = getattr(module, class_name)
        # 创建实例
        instance: BaseRapidapi = cls()
        return instance
    else:
        logger.debug(f"Class {class_name} not found.")


def create_instance_and_pikpak_req(url):
    # 遍历集合并创建实例
    for name in class_names.keys():
        instance = _getInstanceClass(name)
        try:
            return instance.pikpak_req(url)
        except Exception as e:
            logger.debug(f"google 注册验证 当前验证模块失败:{name}\nException:{e}")
    raise Exception("都没成功验证")


def create_instance_and_pikpak_rewardVip():
    # 遍历集合并创建实例
    for name in class_names.keys():
        instance = _getInstanceClass(name)
        try:
            return instance.pikpak_rewardVip()
        except Exception as e:
            logger.debug(f"google 获取vip 当前验证模块失败:{name}\nException:{e}")
    raise Exception("都没成功验证")
