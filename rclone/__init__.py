from abc import abstractmethod
from dataclasses import dataclass
import enum
import os
from pyrclone import Rclone as PyRclone,  RcloneError, RcloneOutput
import json
from typing import Iterable, List, Optional, Tuple


cache_json_file = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "rclone.json")

# logging.basicConfig(level=logging.DEBUG)

rclone_service_content_str = """
[Unit]
Description=remote_name Rclone挂在路径是:mount_path  这个文件由代码生成
After=network.target #alist.service
#Requires=alist.service

[Service]
ExecStartPre=/bin/sleep 5
Type=simple
ExecStop=/bin/fusermount -uz mount_path
User=rclone
RestartForceExitStatus=3
#Restart=always

# 编辑
ExecStart=rclone mount remote_name:/ mount_path --cache-dir=/tmp/alist_cache/auto_remote_name --use-mmap --umask 000 --allow-other --allow-non-empty --dir-cache-time 10m --vfs-cache-mode full --vfs-read-chunk-size 1M --vfs-read-chunk-size-limit 16M --checkers=4 --transfers=1 --vfs-cache-max-size 10G
# 搜库
#ExecStart=rclone mount remote_name:/ mount_path --cache-dir=/tmp/alist_cache/auto_remote_name --use-mmap --umask 000 --allow-other --allow-non-empty --dir-cache-time 24h --vfs-cache-mode full --vfs-read-chunk-size 1M --vfs-read-chunk-size-limit 16M --checkers=4 --transfers=1 --vfs-cache-max-size 10G
# 播放
#ExecStart=rclone mount remote_name:/ mount_path --cache-dir=/tmp/alist_cache/auto_remote_name --use-mmap --umask 000 --allow-other --allow-non-empty --dir-cache-time 24h --vfs-cache-mode full --buffer-size 512M --vfs-read-chunk-size 16M --vfs-read-chunk-size-limit 64M --checkers=4 --transfers=1 --vfs-cache-max-size 10G

[Install]
WantedBy=multi-user.target
"""


class State(enum.Enum):
    static = 0
    enabled = 1
    disabled = -1

    def __str__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @classmethod
    def _missing_(cls, value):
        if type(value) is str:
            value = value.lower()
            if value in dir(cls):
                return cls[value]

        raise ValueError("%r is not a valid %s" % (value, cls.__name__))


@dataclass
class Service:
    unit: str
    state: State
    vendor_preset: State


class Rclone(PyRclone):

    """rclone 名字
    """
    remote: str
    """需要挂在的目录
    """
    mount_path: str

    remote_type: str

    def __init__(self, remote: str = None, mount_path: str = None) -> None:
        """_summary_

        Args:
            remote (str): 名字
            mount_path (str): 需要挂在的目录
        """
        super().__init__()
        if remote == None or remote == "":
            raise Exception("创建rclone错误 remote 没有有效值")
        if mount_path == None or mount_path == "":
            raise Exception("创建rclone错误 mount_path 没有有效值")
        self.remote = remote
        self.mount_path = mount_path

    def get_info(self) -> dict:
        """获取指定远程明的信息

        Returns:
            dir: 获取到的信息
        """
        if not self.remote:
            self.logger.debug("没有指定 remote")
            return None
        result = self.command(command="config", arguments=[
            "userinfo", f"{self.remote}:", "--json"])
        self.logger.debug(result)
        out_str = ""
        for __str in result.output:
            out_str += __str
        if out_str == "":
            return None
        json_data = json.loads(out_str)
        self.logger.debug(json_data)
        return json_data

    def _is_save_2_config(self) -> bool:
        """判断自己是否存在

        Returns:
            bool: 存在True 不存在False
        """
        for remote in self.config.remotes:
            if remote.name == self.remote:
                return True
        return False

    @abstractmethod
    def _create_conf_self(self):
        self.logger.debug("创建config配置 。。需要在子类中重写")

    @abstractmethod
    def _update_conf_self(self):
        """更新配置对应的用户名和密码
        """
        # result = self.rclone.command(command="config", arguments=[
        #     "update", self.remote])
        # print(result)
        self.logger.debug("刷新config中的配置 。。需要在子类中重写")

    def save_self_2_config(self):
        """把自己保存到rclone的配置中 如果不存在则创建存在则更新
        """
        self.logger.info(f"这里保存自己的内容到rclone配置中")
        if self._is_save_2_config():
            self._update_conf_self()
        else:
            self._create_conf_self()

    @abstractmethod
    def _create_conf_self(self):
        """创建 conifg 需要在子类中重写
        """
        self.logger.debug("创建config配置 。。需要在子类中重写")

    def get_systcemctl_all(self) -> List[Service]:
        """获取系统中的rclone服务
        """
        command = ["systemctl", "list-unit-files"]
        result = self._execute(command)
        services: List[Service] = []
        for service in result.output:
            if "rclone" in service:
                service = service.split()
                data = Service(service[0], State(
                    service[1]), State(service[2]))
                services.append(data)
        self.logger.debug(services)
        return services

    def create_service_2_system(self):
        """新建service到系统中
        """
        self.logger.info(
            f"新建service到系统中\nremote_name:{self.remote}\nmount_path:{self.mount_path}")
        if not self.mount_path:
            self.logger.error("不存在 挂载路径 先设置挂载路径在创建")
            return
        if not self.remote:
            self.logger.error(f"rclone 远程不对 remote:{self.remote}")
            return
        if not os.path.exists(self.mount_path) or not os.path.isdir(self.mount_path):
            os.makedirs(self.mount_path)
        service_file_name = f"{self.remote}_rclone.service"
        service_file_path = f"/usr/lib/systemd/system/{service_file_name}"
        service_content = rclone_service_content_str.replace(
            "remote_name", self.remote).replace("mount_path", self.mount_path)
        self.logger.debug(
            f"当前的:\n{service_file_path}\n文件内容:\n\n{service_content}")

        with open(service_file_path, mode="w") as service_file:
            service_file.read(service_content)
        result = self._execute(["systemctrl", "start", service_file_name])
        # self.logger.error(result.error)
        result = self._execute(["systemctrl", "status", service_file_name])
        self.logger.debug(result.output)

    def get_service(self) -> Service:
        """检测此电脑系统中是否有对应的服务

        Returns:
            bool: 存在True 不存在False
        """
        if not self.remote:
            return False
        service_name = f"{self.remote}_rclone.service"
        for service in self.get_systcemctl_all():
            if service.unit == service_name:
                return service
        return None

    def start_system_mount_service(self):
        """开启此rclone的系统服务

        Returns:
            _type_: _description_
        """

        # 检测此服务器是否存在
        service = self.get_service()
        if service:
            if service.state == State.enabled:
                self.logger.info(f"{self.remote}的服务运行中。。。。")
            else:
                # 开启Service
                command = ["systemctl", "start", service.unit]
                result = self._execute(command)
                self.logger.info(f"{self.remote}的服务开启中。。。")
                self.logger.debug(result)
                result = self._execute(["systemctrl", "status", service.unit])
                self.logger.debug(result)
                return
        else:
            self.create_service_2_system()

    def stop_system_mount_service(self):
        """关闭系统挂载服务
        """
        service = self.get_service()
        if not service:
            self.logger.info(f"{self.remote}的服务不存在 不需要关闭")
        else:
            if service.state == State.enabled:
                # 关闭Service
                command = ["systemctl", "stop", service.unit]
                result = self._execute(command)
                self.logger.info(f"{self.remote}的服务关闭中。。。")
                self.logger.debug(result)
                result = self._execute(["systemctrl", "status", service.unit])
                self.logger.debug(result)
            else:
                self.logger.info(
                    f"{self.remote}的服务当前状态{service.state.name} 不需要关闭")


class BaseJsonData():
    remote = None
    mout_path = None

    def __init__(self, json_data: None) -> None:
        if json_data:
            self.__dict__ = json_data


class PikPakJsonData(BaseJsonData):
    pikpak_user = None
    pikpak_password = None

    def __init__(self, json_data: None) -> None:
        if json_data:
            self.__dict__ = json_data


class PikPakRclone(Rclone):
    user: str
    password: str

    def __init__(self, remote: str, mount_path: str, user: str, password: str) -> None:
        super().__init__(remote, mount_path)
        self.user = user
        self.password = password
        self.remote_type = "pikpak"

    def _create_conf_self(self):
        self.logger.debug(
            f"创建Rclone配置 Pikpak \nremote:{self.remote}\nuser:{self.user}\npassword:这里不显示密码")
        result = self.rclone.command(command="config", arguments=[
            "create", self.remote, self.remote_type, f"user={self.user}", f"pass={self.password}"])
        self.logger.debug(result)

    def _update_conf_self(self):
        """更新配置对应的用户名和密码
        """
        self.logger.info(
            f"更新Rclone配置 Pikpak \nremote:{self.remote}\nuser:{self.user}\npassword:这里不显示密码")
        result = self.rclone.command(command="config", arguments=[
            "update", self.remote, f"user={self.user}", f"pass={self.password}"])
        self.logger.debug(result)


def conifg_2_pikpak_rclone(conifg: PikPakJsonData) -> PikPakRclone:
    return PikPakRclone(remote=conifg.get(
        "remote"), mount_path=conifg.get("mout_path"), user=conifg.get("pikpak_user"), password=conifg.get("pikpak_password"))


def get_save_json_config() -> List[PikPakJsonData]:
    """获取本地保存的 rclone json配置表"""
    mount_config: List[PikPakJsonData] = []
    try:
        with open(cache_json_file, mode="r", encoding="utf-8") as file:
            mount_config = json.load(file, object_hook=PikPakJsonData)
    except:
        pass
    return mount_config


def save_config(mount_config: List[PikPakJsonData]):
    """保存 rclone json配置表"""
    with open(cache_json_file, mode='w', encoding="utf-8") as file:
        file.write(json.dumps(
            mount_config, default=lambda o: o.__dict__, ensure_ascii=False, indent=4))


def main():
    rclone_config = get_save_json_config()
    # try:
    #     pikpak_rclone = conifg_2_pikpak_rclone(rclone_config.pop())
    # except:
    #     pikpak_rclone = None
    # with pikpak_rclone:
    #     if pikpak_rclone.get_info().get("VIPType") == "novip":
    #         pass
    # rclone_config[0].pikpak_user = rclone_config[0].pikpak_user + "090909090"
    # save_config(rclone_config)


if __name__ == "__main__":
    main()
