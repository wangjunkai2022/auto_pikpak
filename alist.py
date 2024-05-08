import requests
from config import alist_domain, alist_pd, alist_user
import json


class Alist:
    token = ""
    user, pd = None, None

    def __init__(self, user, pd) -> None:
        self.user = user
        self.pd = pd
        self.__update_token()

    def __update_token(self):
        url = f"{alist_domain}/api/auth/login"
        payload = {
            "username": self.user,
            "password": self.pd,
        }
        headers = {
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        data_json = response.json()
        if response.status_code == 200:
            self.token = data_json["data"].get("token")
        print(data_json)

    def get_storage_list(self):
        url = f"{alist_domain}/api/admin/storage/list"
        payload = {
            "page": "1",
            "per_page": "50",
        }
        headers = {
            "Authorization": self.token,
        }
        response = requests.request("GET", url, json=payload, headers=headers)
        data_json = response.json()
        print(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    def update_storage(self, data):
        url = f"{alist_domain}/api/admin/storage/update"
        payload = data
        headers = {
            "Authorization": self.token,
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        data_json = response.json()
        print(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    # 获取所有的pikpak的账户和密码
    def get_all_pikpak_storage(self):
        storage_list_data = self.get_storage_list()
        pikpaks = []
        for data in storage_list_data.get("content"):
            addition = json.loads(data.get("addition"))
            username = addition.get("username")
            password = addition.get("password")
            pikpaks.append(
                {
                    "username": username,
                    "password": password,
                }
            )
        return pikpaks

if __name__ == "__main__":
    alist = Alist(alist_user, alist_pd)
    # storage_list_data = alist.get_storage_list()
    # import config
    # invites = config.pikpak_user
    # for data in storage_list_data.get("content"):
    #     addition = json.loads(data.get("addition"))
    #     if addition.get("username") == invites[0].get("mail"):
    #         # addition["username"] = "test@test.com"
    #         data["addition"] = json.dumps(addition)
    #         print(data)
    #         alist.update_storage(data)
    #     print(addition)

    pikpaks = alist.get_all_pikpak_storage()
    print(pikpaks)
