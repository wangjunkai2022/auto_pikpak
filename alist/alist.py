import copy
import datetime
import logging
import os
from typing import List
import requests
from config.config import alist_domain, alist_pd, alist_user
import json
logger = logging.getLogger("alist")


class JsonDataStorage():
    id = None
    mount_path = None
    order = None
    driver = None
    cache_expiration = None
    status = None
    addition = None
    remark = None
    modified = None
    disabled = None
    enable_sign = None
    order_by = None
    order_direction = None
    extract_folder = None
    web_proxy = None
    webdav_policy = None
    proxy_range = None
    down_proxy_url = None

    def __init__(self, json_data: dict = None) -> None:
        if json_data:
            self.__dict__ = json_data


class Alist(object):
    token = ""
    user, pd = None, None
    _domain = None
    cache_json_file = os.path.abspath(__file__)[:-2] + "json"

    def saveToNowConif(self):
        """保存一下当前配置到本地路径
        """
        try:
            with open(self.cache_json_file, mode='r') as file:
                json_data = json.load(file)
        except:
            json_data = []
        data = {}
        data["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["content"] = self.get_storage_list()["content"]
        json_data.append(data)
        with open(self.cache_json_file, mode='w') as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)

    def _get_header(self):
        return {
            "Authorization": self.token,
        }

    def __request(self, method, url, **kwargs,):
        kwargs["verify"] = False
        kwargs["headers"] = self._get_header()
        return requests.request(method, url, **kwargs)

    def __init__(self, user=alist_user, pd=alist_pd, domain=alist_domain) -> None:
        self.user = user
        self.pd = pd
        self._domain = domain
        self.__update_token()

    def __update_token(self):
        url = f"{self._domain}/api/auth/login"
        payload = {
            "username": self.user,
            "password": self.pd,
        }
        response = self.__request("POST", url, json=payload)
        data_json = response.json()
        if response.status_code == 200:
            self.token = data_json["data"].get("token")
        logger.debug(data_json)

    def get_storage_list(self):
        url = f"{self._domain}/api/admin/storage/list"
        payload = {
            "page": "1",
            "per_page": "50",
        }
        response = self.__request("GET", url, json=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    def create_storage(self, data: dict) -> None:
        """新建存储库

        Args:
            data (dict): 需要创建的库数据

        Returns:
            _type_: _description_
        """
        url = f"{self._domain}/api/admin/storage/create"
        payload = data
        response = self.__request("POST", url, json=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    def update_storage(self, data: dict) -> None:
        """修改存储库

        Args:
            data (dict): 需要修改的库

        Returns:
            _type_: _description_
        """
        url = f"{self._domain}/api/admin/storage/update"
        payload = data
        response = self.__request("POST", url, json=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    # 删除库
    def delete_storage(self, id: str) -> None:
        """删除指定存储库

        Args:
            id (str): 需要删除的id

        Returns:
            _type_: _description_
        """
        url = f"{self._domain}/api/admin/storage/delete"
        payload = {
            "id": id,
        }
        response = self.__request("POST", url, params=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    # 获取所有的pikpak的账户和密码

    def get_all_pikpak_storage(self) -> List[dict]:
        """获取所有的pikpak的账户和密码

        Returns:
            _type_: _description_
        """
        storage_list_data = self.get_storage_list()
        pikpaks: List[dict] = []
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

    def copy_storages_2_alist(self, to_alist_go: object, is_clean: bool = False) -> None:
        """把此所有储存库复制到另外一个Alist中

        Args:
            to_alist_go (Alist): 需要复制到的Alist
            is_clean (bool, optional): 是否清空以前的数据. Defaults to False.
        """
        __to_alist_go = to_alist_go
        if is_clean:
            for _to_storage in __to_alist_go.get_storage_list().get("content"):
                __to_alist_go.delete_storage(_to_storage.get("id"))
        for self_storage in self.get_storage_list().get("content"):
            _mount_path = self_storage.get("mount_path")
            _have_mount_path = False
            for _to_storage in __to_alist_go.get_storage_list().get("content"):
                if _mount_path == _to_storage.get("mount_path"):
                    # __to_alist_go.delete_storage(_to_storage.get("id"))
                    _new_storage = copy.deepcopy(self_storage)
                    _new_storage["id"] = _to_storage.get("id")
                    __to_alist_go.update_storage(_new_storage)
                    _have_mount_path = True
                    break
            if _have_mount_path:
                continue
            _new_storage = copy.deepcopy(self_storage)
            _new_storage["id"] = None
            __to_alist_go.create_storage(_new_storage)


if __name__ == "__main__":
    alist = Alist()
    # storage_list_data = alist.get_storage_list()
    # import config
    # invites = config.pikpak_user
    # for data in storage_list_data.get("content"):
    #     addition = json.loads(data.get("addition"))
    #     if addition.get("username") == invites[0].get("mail"):
    #         # addition["username"] = "test@test.com"
    #         data["addition"] = json.dumps(addition)
    #         logger.debug(data)
    #         alist.update_storage(data)
    #     logger.debug(addition)

    # pikpaks = alist.get_storage_list()
    # logger.debug(pikpaks)
    alist.copy_storages_2_alist(
        Alist(domain="http://10.211.55.58:5244"), is_clean=True)
    # alist.saveToNowConif()

    # alist=Alist(domain="http://10.211.55.58:5244").copy_storages_2_alist(Alist())
