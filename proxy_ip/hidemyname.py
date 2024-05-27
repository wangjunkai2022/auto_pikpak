# https://hidemyname.io/cn/proxy-list/
import json
import re
import time

import requests


class hidemyname:
    domain = "hidemyname.io"
    cookie = "t=384151002; sbjs_migrations=1418474375998%3D1; sbjs_first_add=fd%3D2024-05-08%2020%3A07%3A08%7C%7C%7Cep%3Dhttps%3A%2F%2Fhidemyname.io%2Fcn%2Fproxy-list%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F; sbjs_current=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_first=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Safari%2F537.36; CookieConsent={stamp:%27-1%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:1%2Cutc:1715173629272%2Cregion:%27HK%27}; _ga=GA1.1.45043217.1715173630; PAPVisitorId=124704a5f07f176652012611bf9e4VDk; _ym_uid=1715173630491925500; _ym_d=1715173630; cjConsent=MHxOfDB8Tnww; cjUser=3ebbdf46-5dcb-4be0-839d-dcc4c8ffebef; _ym_isad=1; _tt_enable_cookie=1; _ttp=Ucni13rXFmgPG3rFO6OTht1o3vp; _ym_visorc=w; sbjs_current_add=fd%3D2024-05-08%2020%3A09%3A33%7C%7C%7Cep%3Dhttps%3A%2F%2Fhidemyname.io%2Fcn%2Fproxy-list%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F; sbjs_session=pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fhidemyname.io%2Fcn%2Fproxy-list%2F; _ga_KJFZ3PJZP3=GS1.1.1715173629.1.1.1715173773.41.0.0"
    headers = {
        "Upgrade-Insecure-Requests": '1',
        "Sec-Fetch-Site": 'same-origin',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "content-type": "application/json; charset=utf-8",

        "Accept-Encoding": "gzip, deflate, br, zstd",
        'Accept-Language': "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        # "Referer":"https://hidemyname.io/cn/proxy-list/?start=64",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
    }

    def __getToken(self):
        cookies_dict = {}
        for cookie in self.cookie.split('; '):
            cookies_dict[cookie.split('=')[0]] = cookie.split('=')[-1]
        return cookies_dict

    def get_proxy_list(self):
        proxy_ips = []
        ips = []
        for index in range(61, 100):
            url = f"https://{self.domain}/cn/proxy-list/"
            try:
                response = requests.request("GET", url,
                                            cookies=self.__getToken(),
                                            headers=self.headers,
                                            )
            except:
                continue
            html_doc = str(response.content, 'utf-8')
            re_search = re.search(
                r"const fpsList = \[\{(.*)\}\];", response.text)
            if re_search:
                str_ = re_search.group()[len("const fpsList = "):-1]
                data = json.loads(str_)
                for _data in data:
                    ip = _data.get('ip')
                    if ip in ips:
                        continue
                    proxy_ips.append(f"{ip}:{_data.get('port')} http")
                    ips.append(ip)

            time.sleep(0.5)
        return proxy_ips


if __name__ == '__main__':
    hidemyname().get_proxy_list()
    # file = open("../test.txt", mode="r")
    # str_ = file.read()
    # file.close()
    # print(str_)
    # re_search = re.search(r"const fpsList = \[\{(.*)\}\];", str_)
    # if re_search:
    #     str_ = re_search.group()[len("const fpsList = "):-1]
    #     data = json.loads(str_)
    #     print(str_)
