import copy
import datetime
import logging
import os
from typing import List
import requests
from config.config import alist_domain, alist_pd, alist_user
import json
logger = logging.getLogger("alist")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


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
        temp_datas = []

        new_json_data = []
        for _data in json_data:
            __json_data = []
            for __data in _data["content"]:
                if __data in temp_datas:
                    continue
                else:
                    temp_datas.append(__data)
                    __json_data.append(__data)
            if len(__json_data) > 0:
                new_json_data.append(
                    {
                        "content": __json_data,
                        "time": _data["time"],
                    }
                )
        __json_data = []
        for _data in data["content"]:
            if _data in temp_datas:
                continue
            else:
                __json_data.append(_data)
        if len(__json_data) > 0:
            new_json_data.append(
                {
                    "content": __json_data,
                    "time": data["time"],
                }
            )
        with open(self.cache_json_file, mode='w') as file:
            json.dump(new_json_data, file, ensure_ascii=False, indent=4)

    def _get_header(self):
        return {
            "Authorization": self.token,
        }

    def __request(self, method, url, **kwargs,):
        kwargs["verify"] = False
        kwargs["headers"] = self._get_header()
        try:
            response = requests.request(method, url, **kwargs)
            if response.json().get("code") == 401:
                self.__update_token()
                return self.__request(method, url, **kwargs,)
            return response
        except Exception as e:
            logger.error(f"alist 请求报错了{url}")
            raise e

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

    def update_load_all_storage(self):
        url = f"{self._domain}/api/admin/storage/load_all"
        payload = {
        }
        response = self.__request("POST", url, json=payload)
        data_json = response.json()
        if response.status_code == 200:
            return data_json
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
        else:
            return

    def update_storage(self, data: dict, isAddUpdateTime=True) -> None:
        """修改存储库

        Args:
            data (dict): 需要修改的库
            isAddUpdateTime: 是否需要添加操作时间到备注中
        Returns:
            _type_: _description_
        """
        if isAddUpdateTime:
            remark_str = data.get("remark")
            if remark_str == '':
                remark_str = "{}"
            remark_json = json.loads(remark_str)
            # 获取当前时间
            now = datetime.datetime.now()
            # 将当前时间转换为字符串
            time_string = now.strftime("%Y-%m-%d %H:%M:%S")
            remark_json["update_time"] = time_string
            remark_str = json.dumps(remark_json, ensure_ascii=False, indent=4)
            data['remark'] = remark_str
        url = f"{self._domain}/api/admin/storage/update"
        payload = data
        response = self.__request("POST", url, json=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    # 关闭
    def disable_storage(self, id: str) -> None:
        """关闭指定存储库

        Args:
            id (str): 需要关闭的id

        Returns:
            _type_: _description_
        """
        url = f"{self._domain}/api/admin/storage/disable"
        payload = {
            "id": id,
        }
        response = self.__request("POST", url, params=payload)
        data_json = response.json()
        logger.debug(data_json)
        if response.status_code == 200:
            return data_json.get("data")

    def enable_storage(self, id: str) -> None:
        """开启指定存储库

        Args:
            id (str): 需要开启的id

        Returns:
            _type_: _description_
        """
        url = f"{self._domain}/api/admin/storage/enable"
        payload = {
            "id": id,
        }
        response = self.__request("POST", url, params=payload)
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
            driver = data.get("driver")
            if driver == "PikPak":
                addition = json.loads(data.get("addition"))
                username = addition.get("username")
                password = addition.get("password")
                remark_str = data.get("remark")
                disabled = data.get("disabled")
                if remark_str == "":
                    remark_str = '{}'
                remark_json = json.loads(remark_str,)
                update_time = remark_json.get("update_time", None)
                pikpaks.append(
                    {
                        "username": username,
                        "password": password,
                        "name": data.get("mount_path")[1:],
                        'update_time': update_time,
                        'disabled': disabled,
                        'alist_data': data,
                        'addition': addition,
                    }
                )
        return pikpaks

    def copy_storages_2_alist(self, to_alist_go: object, is_clean: bool = False, isDisible: bool = True) -> None:
        """把此所有储存库复制到另外一个Alist中

        Args:
            to_alist_go (Alist): 需要复制到的Alist
            is_clean (bool, optional): 是否清空以前的数据. Defaults to False.
            isDisible (bool) 复制的存储库在新号中的状态 Defaults to True.
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
            _new_storage['disabled'] = isDisible
            __to_alist_go.create_storage(_new_storage)

    def restore_configuration_file_2_self(self, is_clean: bool = False, is_disible: bool = True):
        """
        恢复配置文件内容到此存储库
        """
        try:
            with open(self.cache_json_file, mode='r') as file:
                json_data = json.load(file)
        except:
            json_data = []
        sorted_data = sorted(json_data, key=lambda x: datetime.datetime.strptime(
            x['time'], "%Y-%m-%d %H:%M:%S"), reverse=True)
        contents, names = [], []
        for data in sorted_data:
            for content in data.get("content"):
                if content.get("mount_path")[1:] in names:
                    continue
                else:
                    names.append(content.get("mount_path")[1:])
                    contents.append(content)
        if is_clean:
            for _to_storage in self.get_storage_list().get("content"):
                self.delete_storage(_to_storage.get("id"))
        for storage in contents:
            storage['disabled'] = is_disible or storage['disabled']
            data = self.create_storage(storage)
            if data:
                print(data)
            else:
                print("ppppp")
    
    def update_storagePK_refresh_token(self, id:str, token:str):
        """
        更新 指定alist pikapk 的存储的 refresh_token
        Args:
            id (str): 需要更新的库的id
            token (str): 新 refresh_token
        """
        storage_list_data = self.get_storage_list()
        for storage in storage_list_data.get("content"):
            driver = storage.get("driver")
            if driver == "PikPak" and storage.get("id") == id:
                addition = json.loads(storage.get("addition"))
                addition["refresh_token"] = token
                platform = addition.get("platform", "")
                if platform == "":
                    addition['platform'] = "android"
                storage['addition'] = json.dumps(addition)
                return self.update_storage(storage, False)


    def set_captcha_url(self, url: str = "http://localhost:5243/api/login", is_disible: bool = True):
        for storage in self.get_storage_list().get("content"):
            driver = storage.get("driver")
            if driver == "PikPak":
                storage['disabled'] = is_disible
                addition = json.loads(storage.get("addition"))
                addition['captcha_api'] = url
                addition['platform'] = 'android'
                addition['refresh_token'] = ''
                storage['addition'] = json.dumps(addition)
                self.update_storage(storage, False)
                # addition
        self.update_load_all_storage()

    # 邮箱是否已经添加到alist中
    def mialIs2Alist(self, mail: str = ""):
        for alist2pkipak in self.get_all_pikpak_storage():
            username = alist2pkipak.get("username")
            name = alist2pkipak.get("name")
            if mail == username:
                logger.debug(f"{mail}已在 Alist:{name}中")
                return True, alist2pkipak
        return False, None

if __name__ == "__main__":
    alist = Alist()
    # alist.saveToNowConif()
    storage_list_data = alist.set_captcha_url()
    print(storage_list_data)
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
        Alist(domain="http://localhost:5244"), is_clean=True)
    # alist.saveToNowConif()

    # alist=Alist(domain="http://10.211.55.58:5244").copy_storages_2_alist(Alist())
