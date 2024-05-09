import json
import os
import re
import time
import requests


class kuaidaili:
    domain = "www.kuaidaili.com"
    cookie = "sid=1713152194329737; _gcl_au=1.1.856872579.1713153534; _gid=GA1.2.118412114.1713153535; __51uvsct__K3h4gFH3WOf3aJqX=1; __51vcke__K3h4gFH3WOf3aJqX=b8477367-46e1-51d0-a551-f2d00f27a672; __51vuft__K3h4gFH3WOf3aJqX=1713153534637; _ss_s_uid=6f6cc3db803b9e33ea78c37798eee83e; channelid=ggtg_D6_D6a9; _gac_UA-76097251-1=1.1713154790.CjwKCAjw_e2wBhAEEiwAyFFFo6QRfvx0h7a7BWc1CUOmNAT4bFhbh7UWnAkezUkG_1U5kCp5S7f3QBoCag8QAvD_BwE; _gcl_aw=GCL.1713154791.CjwKCAjw_e2wBhAEEiwAyFFFo6QRfvx0h7a7BWc1CUOmNAT4bFhbh7UWnAkezUkG_1U5kCp5S7f3QBoCag8QAvD_BwE; _ga_DC1XM0P4JL=GS1.1.1713153534.1.1.1713155229.60.0.0; __vtins__K3h4gFH3WOf3aJqX=%7B%22sid%22%3A%20%22717d04e7-731d-56ed-842c-b0381385c2a2%22%2C%20%22vd%22%3A%2014%2C%20%22stt%22%3A%201694909%2C%20%22dr%22%3A%2055635%2C%20%22expires%22%3A%201713157029544%2C%20%22ct%22%3A%201713155229544%7D; _ga=GA1.2.560805793.1713153534; _gat=1"
    headers = {
        "Upgrade-Insecure-Requests": '1',
        "Sec-Fetch-Site": 'same-origin',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "content-type": "application/json; charset=utf-8",

        "Accept-Encoding": "gzip, deflate, br, zstd",
        'Accept-Language': "zh-CN,zh;q=0.9",

    }

    def __getToken(self):
        cookies_dict = {}
        for cookie in self.cookie.split('; '):
            cookies_dict[cookie.split('=')[0]] = cookie.split('=')[-1]
        return cookies_dict

    cache_json_file = os.path.abspath(__file__)[:-2] + "json"

    def get_proxy_list(self):
        try:
            with open(self.cache_json_file, mode="r", encoding="utf-8") as file:
                json_str = file.read()
                json_data = json.loads(json_str)
        except:
            json_data = {}
        _time = time.time() - json_data.get("time", 0)

        proxy_ips = []
        ips = []

        if _time < 60 * 60 * 6:
            return json_data.get("ips", [])

        for index in range(1, 100):
            url = f"https://{self.domain}/free/fps/{index}/"
            try:
                response = requests.request("GET", url,
                                            cookies=self.__getToken(),
                                            headers=self.headers,
                                            )
            except:
                continue
            re_search = re.search(
                r"const fpsList = \[\{(.*)\}\];", response.text)
            if re_search:
                str_ = re_search.group()[len("const fpsList = "):-1]
                data = json.loads(str_)
                for _data in data:
                    ip = _data.get('ip')
                    # if ip in ips:
                    #     continue
                    proxy_ips.append(f"{ip}:{_data.get('port')} http")
                    ips.append(ip)

            time.sleep(0.5)
            print(response.text)
        json_data = {
            "time": time.time(),
            "ips": proxy_ips,
        }
        with open(self.cache_json_file, mode='w', encoding="utf-8") as file:
            file.write(json.dumps(json_data))
        return proxy_ips


if __name__ == '__main__':
    print(kuaidaili().get_proxy_list())
    # file = open("../test.txt", mode="r")
    # str_ = file.read()
    # file.close()
    # print(str_)
    # re_search = re.search(r"const fpsList = \[\{(.*)\}\];", str_)
    # if re_search:
    #     str_ = re_search.group()[len("const fpsList = "):-1]
    #     data = json.loads(str_)
    #     print(str_)
    # cache_name = os.path.abspath(__file__)[:-2]  # type: ignore
