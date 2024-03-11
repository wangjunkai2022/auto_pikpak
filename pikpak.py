import uuid
import time

import requests


class PikPak:
    client_secret = "dbw2OtmVEeuUvIptb1Coyg"
    mail = ""
    pd = ""
    client_id = "YNxT9w7GMdWvEOKa"
    device_id = str(uuid.uuid4()).replace("-", "")
    device_id2 = str(uuid.uuid4()).replace("-", "")
    captcha_token = ""
    verification_id = ''
    mail_code = ""
    proxies = None
    user_id = None
    authorization = None

    country = "US"
    language = "zh-TW"

    def set_proxy(self, proxy):
        if not proxy.startswith("http://"):
            proxy = f"http://{proxy}"
        self.proxies = {
            "http": proxy,
            "https": proxy,
        }

    def __user_agent(self):
        # 创建随机UA
        t = time.time()
        ua = f"ANDROID-com.pikcloud.pikpak/1.42.6 accessmode/ devicename/Samsung_Sm-g988n appname/android-com.pikcloud.pikpak appid/ action_type/ clientid/{self.client_id} deviceid/{self.device_id} refresh_token/ grant_type/ devicemodel/SM-G988N networktype/WIFI accesstype/ sessionid/ osversion/7.1.2 datetime/{int(round(t * 1000))} protocolversion/200 sdkversion/2.0.1.200200 clientversion/1.42.6 providername/NONE clientip/ session_origin/ devicesign/div101.{self.device_id}{self.device_id2} platformversion/10 usrno/"
        return ua

    def __init__(self, mail, pd):
        self.mail = mail
        self.pd = pd

    # 手动设置验证token 用于第三方或者手动验证后操作
    def set_captcha_token(self, captcha_token):
        self.captcha_token = captcha_token

    def __initCaptcha(self):
        url = "https://user.mypikpak.com/v1/shield/captcha/init"
        payload = {
            "client_id": self.client_id,
            "action": self.captcha_token == "" and "POST:/v1/auth/verification" or "POST:/v1/auth/signin",
            "device_id": self.device_id,
            "captcha_token": self.captcha_token,
            "redirect_uri": "xlaccsdk01://xunlei.com/callback?state=dharbor",
            "meta": {
                "email": self.mail,
                "user_id": self.user_id,
                "client_version": "1.42.6",
                "package_name": "com.pikcloud.pikpak",
            }
        }
        headers = {
            "x-device-id": self.device_id,
            "accept-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",

            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        print(f"__initCaptcha\n{res_json}")
        if res_json.get("url"):
            print("打开这个网址手动去执行验证 并获取的token复制到此\n")
            token = input()
            print(f"输入的token\n{token}")
            self.captcha_token = token
        else:
            if res_json.get("error") == "captcha_invalid":
                self.__initCaptcha()
                return
            self.captcha_token = res_json.get("captcha_token")

    def send_code(self):
        url = f"https://user.mypikpak.com/v1/auth/verification"
        payload = {
            "client_id": self.client_id,
            "captcha_token": self.captcha_token,
            "email": self.mail,
            "locale": self.language,
            "target": "ANY",
        }
        headers = {
            "x-device-id": self.device_id,
            "accept-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",

            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        if response.status_code != 200:
            print(f"发送验证消息到邮箱 ERROR:\n{res_json}")
            if res_json.get("error") == "captcha_required":
                self.captcha_token = ''
                self.__initCaptcha()
                self.send_code()
        else:
            self.verification_id = res_json.get("verification_id")
            print(f"发送验证消息到邮箱:\n{res_json}")

    # 设置获取的邮箱的验证码
    def set_mail_2_code(self, code=""):
        if code == "":
            code = str(input("请输入邮箱中的验证码\n"))
        url = "https://user.mypikpak.com/v1/auth/verification/verify"
        payload = {
            "client_id": self.client_id,
            "verification_id": self.verification_id,
            "verification_code": code,
        }
        headers = {
            "x-device-id": self.device_id,
            "accept-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",

            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies, verify=False)
        res_json = response.json()
        if response.status_code == 200:
            self.verification_id = res_json.get("verification_token")
            self.mail_code = code
            print(f"设置邮箱的验证码:\n{res_json}")
        else:
            print(f"设置邮箱的验证码 ERROR:\n{res_json}")

    def signup(self):
        url = "https://user.mypikpak.com/v1/auth/signup"
        payload = {
            "client_id": self.client_id,
            "captcha_token": self.captcha_token,
            "client_secret": self.client_secret,
            "email": self.mail,
            "name": self.mail.split("@")[0],
            "password": self.pd,
            "verification_token": self.verification_id,
        }
        headers = {
            "x-device-id": self.device_id,
            "accept-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",

            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        if response.status_code != 200:
            print(f"注册登陆失败:\n{res_json}")
            if res_json.get("error") == "captcha_invalid":
                self.__initCaptcha()
                # self.set_mail_2_code(self.mail_code)
                self.signup()
            elif res_json.get("error") == "already_exists":
                print(f"用户存在\n{res_json}")
                self.login()
        else:
            print(f"注册登陆成功:\n{res_json}")
            self.user_id = res_json.get("sub")
            self.authorization = f"{res_json.get('token_type')} {res_json.get('access_token')}"

    def login(self):
        url = "https://user.mypikpak.com/v1/auth/signin"
        payload = {
            "client_id": self.client_id,
            "captcha_token": self.captcha_token,
            "client_secret": self.client_secret,
            "username": self.mail,
            "password": self.pd,
        }
        headers = {
            "x-device-id": self.device_id,
            "x-peer-id": self.device_id,
            "x-captcha-token": self.captcha_token,
            "x-client-version-code": "10181",
            "x-alt-capability": "3",
            "accept-language": self.language,
            "country": self.country,
            "x-user-region": "2",
            "product_flavor_name": "cha",
            "x-system-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",
            "Authorization": self.authorization,
            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        if response.status_code == 200:
            print(f"登陆成功{res_json}")
            self.user_id = res_json.get("sub")
            self.authorization = f"{res_json.get('token_type')} {res_json.get('access_token')}"
        else:
            # if res_json.get("error") == "captcha_invalid":
            #     self.__initCaptcha()
            #     self.login()
            print(f"登陆失败{res_json}")

    def get_active_invite(self):
        url = "https://api-drive.mypikpak.com/vip/v1/activity/invite"
        payload = {
            "data": {
                "sdk_int": "25",
                "uuid": self.device_id,
                "userType": "1",
                "userid": self.user_id,
                "userSub": "",
                "product_flavor_name": "cha",
                "language_system": self.language,
                "language_app": self.language,
                "build_version_release": "7.1.2",
                "phoneModel": "SM-G988N",
                "build_manufacturer": "SAMSUNG",
                "build_sdk_int": "25",
                "channel": "official",
                "versionCode": "10180",
                "versionName": "1.42.6",
                "installFrom": "other",
                "country": self.country,
            },
            "apk_extra": {"channel": "official"},
        }
        headers = {
            "x-device-id": self.device_id,
            "x-peer-id": self.device_id,
            "x-captcha-token": self.captcha_token,
            "x-client-version-code": "10181",
            "x-alt-capability": "3",
            "accept-language": self.language,
            "country": self.country,
            "x-user-region": "2",
            "product_flavor_name": "cha",
            "x-system-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",
            "Authorization": self.authorization,
            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("GET", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        if response.status_code != 200:
            if res_json.get("error") == "captcha_invalid":
                self.__initCaptcha()
                self.get_active_invite()
            return
        print(f"vip邀请信息返回:\n{res_json}")

    # 设置邀请
    def set_activation_code(self, code):
        url = "https://api-drive.mypikpak.com/vip/v1/order/activation-code"
        payload = {
            "activation_code": str(code),
            "page": "invite",
        }
        headers = {
            "x-device-id": self.device_id,
            "x-peer-id": self.device_id,
            "x-captcha-token": self.captcha_token,
            "x-client-version-code": "10181",
            "x-alt-capability": "3",
            "accept-language": self.language,
            "country": self.country,
            "x-user-region": "2",
            "product_flavor_name": "cha",
            "x-system-language": self.language,
            "User-Agent": self.__user_agent(),
            "content-type": "application/json; charset=utf-8",
            "Authorization": self.authorization,
            "Accept-Encoding": "deflate, gzip"
        }

        response = requests.request("POST", url, json=payload, headers=headers, proxies=self.proxies)
        res_json = response.json()
        if response.status_code != 200:
            if res_json.get("error") == "captcha_invalid":
                self.__initCaptcha()
                self.set_activation_code(code)
            return
        print(f"填写邀请结果返回:\n{res_json}")


if __name__ == "__main__":
    email = "gexijiv324@azduan.com"
    password = "098poi"
    pikpak_ = PikPak(email, password)
    pikpak_.set_proxy("218.6.120.111:7777")
    pikpak_.send_code()
    pikpak_.set_mail_2_code()
    pikpak_.signup()
    time.sleep(5)
    pikpak_.set_activation_code(98105081)
