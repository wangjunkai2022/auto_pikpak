from abc import abstractmethod
from dataclasses import dataclass
import enum
import logging
import os
import threading
import time
from pyrclone import Rclone as PyRclone,  RcloneError, RcloneOutput
import json
from typing import Iterable, List, Optional, Tuple

logger: logging.Logger = logging.getLogger("Rclone")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

cache_json_file = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "rclone.json")

# logger.setLevel(level=logging.DEBUG)
service_file_path_root = "/etc/systemd/system/ubuntu.target.wants"
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

    def is_mount(self) -> bool:
        """判断系统中是否挂载了自己
        Returns:
            bool: 存在是True 不存在是False
        """
        if os.path.exists(self.mount_path):
            return len(os.listdir(self.mount_path)) > 0
        else:
            return False

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
            logger.debug("没有指定 remote")
            return None
        if not self._is_save_2_config():
            return None
            # self._create_conf_self()
            # time.sleep(60)
        result = self.command(command="config", arguments=[
            "userinfo", f"{self.remote}:", "--json"])
        logger.debug(result)
        out_str = ""
        for __str in result.output:
            out_str += __str
        if out_str == "":
            return None
        json_data = json.loads(out_str)
        logger.debug(json_data)
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
        logger.debug("创建config配置 。。需要在子类中重写")

    @abstractmethod
    def _update_conf_self(self):
        """更新配置对应的用户名和密码
        """
        # result = self.rclone.command(command="config", arguments=[
        #     "update", self.remote])
        # print(result)
        logger.debug("刷新config中的配置 。。需要在子类中重写")

    def save_self_2_config(self):
        """把自己保存到rclone的配置中 如果不存在则创建存在则更新
        """
        logger.info(f"这里保存自己的内容到rclone配置中")
        if self._is_save_2_config():
            self._update_conf_self()
        else:
            self._create_conf_self()

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
        logger.debug(services)
        return services

    def create_service_2_system(self):
        """新建service到系统中
        """
        logger.info(
            f"新建service到系统中\nremote_name:{self.remote}\nmount_path:{self.mount_path}")
        if not self.mount_path:
            logger.error("不存在 挂载路径 先设置挂载路径在创建")
            return
        if not self.remote:
            logger.error(f"rclone 远程不对 remote:{self.remote}")
            return
        if not os.path.exists(self.mount_path) or not os.path.isdir(self.mount_path):
            os.makedirs(self.mount_path)
        service_file_name = f"{self.remote}_rclone.service"
        service_file_path = os.path.join(
            service_file_path_root, service_file_name)
        service_content = rclone_service_content_str.replace(
            "remote_name", self.remote).replace("mount_path", self.mount_path)
        logger.debug(
            f"当前的:\n{service_file_path}\n文件内容:\n\n{service_content}")

        with open(service_file_path, mode="w") as service_file:
            service_file.write(service_content)
        result = self._execute(["systemctl", "start", service_file_name])
        # logger.error(result.error)
        result = self._execute(["systemctl", "status", service_file_name])
        logger.debug(result.output)

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
                logger.info(f"{self.remote}的服务运行中。。。。")
            else:
                # 开启Service
                command = ["systemctl", "start", service.unit]
                result = self._execute(command)
                logger.info(f"{self.remote}的服务开启中。。。")
                logger.debug(result)
                result = self._execute(["systemctl", "status", service.unit])
                logger.debug(result)
                return
        else:
            self.create_service_2_system()

    def stop_system_mount_service(self):
        """关闭系统挂载服务
        """
        service = self.get_service()
        if not service:
            logger.info(f"{self.remote}的服务不存在 不需要关闭")
        else:
            if service.state == State.enabled:
                # 关闭Service
                command = ["systemctl", "stop", service.unit]
                result = self._execute(command)
                logger.info(f"{self.remote}的服务关闭中。。。")
                logger.debug(result)
                result = self._execute(["systemctl", "status", service.unit])
                logger.debug(result)
            else:
                logger.info(
                    f"{self.remote}的服务当前状态{service.state.name} 不需要关闭")

    def __th_mount(self):
        result = self.command("mount", [
            f"{self.remote}:/",
            f"{self.mount_path}",
            "--cache-dir=/tmp/alist_cache/auto_remote_name",
            "--use-mmap",
            "--umask=000",
            "--allow-other",
            "--allow-non-empty",
            "--dir-cache-time=10m",
            "--vfs-cache-mode=full",
            "--vfs-read-chunk-size=1M",
            "--vfs-read-chunk-size-limit=16M",
            "--checkers=4",
            "--transfers=1",
            "--vfs-cache-max-size=10G",
            "--daemon",
        ])
        logger.debug(result)

    mount_th: threading.Thread = None

    def run_mount(self):
        """挂载pikpak
        """
        # if self.mount_th and not self.mount_th.isDaemon():
        #     logger.info(f"当前rclone已经挂载了")
        #     return
        # self.mount_th = threading.Thread(target=self.__th_mount)
        # self.mount_th.start()
        logger.debug(f"挂载{self.remote} 到{self.mount_path}")
        if self.is_mount:
            self.stop_mount()
        if not os.path.exists(self.mount_path):
            os.makedirs(self.mount_path)
        self.__th_mount()
        # while True:
        #     time.sleep(1)
        #     print("循环主线程")

    def stop_mount(self):
        # if self.mount_th and not self.mount_th.isDaemon():
        #     logger.info(f"关闭挂载进程")
        logger.info("尝试卸载已经挂载")
        result = self._execute(["fusermount", "-uz", self.mount_path])
        if result.return_code == 0:
            logger.info("卸载成功")
        else:
            logger.info(result)


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
        logger.info(
            f"创建Rclone配置 Pikpak \nremote:{self.remote}\nuser:{self.user}\npassword:这里不显示密码")
        result = self.command(command="config", arguments=[
            "create", self.remote, self.remote_type, f"user={self.user}", f"pass={self.password}"])
        logger.debug(result)

    def _update_conf_self(self):
        """更新配置对应的用户名和密码
        """
        logger.info(
            f"更新Rclone配置 Pikpak \nremote:{self.remote}\nuser:{self.user}\npassword:这里不显示密码")
        result = self.command(command="config", arguments=[
            "update", self.remote, f"user={self.user}", f"pass={self.password}"])
        logger.debug(result)


class RCloneManager:
    json_config: List[PikPakJsonData] = []

    def __init__(self) -> None:
        self._get_save_json_config()

    def conifg_2_pikpak_rclone(self, config: PikPakJsonData) -> PikPakRclone:
        return PikPakRclone(remote=config.remote, mount_path=config.mout_path, user=config.pikpak_user, password=config.pikpak_password)

    def _get_save_json_config(self):
        """获取本地保存的 rclone json配置表"""
        try:
            with open(cache_json_file, mode="r", encoding="utf-8") as file:
                self.json_config = json.load(file, object_hook=PikPakJsonData)
        except:
            pass

    def save_config(self):
        """保存 rclone json配置表"""
        with open(cache_json_file, mode='w', encoding="utf-8") as file:
            file.write(json.dumps(
                self.json_config, default=lambda o: o.__dict__, ensure_ascii=False, indent=4))


def main():
    logger.debug("Main")
    rclone_manager = RCloneManager()
    for config in rclone_manager.json_config:
        rclone = rclone_manager.conifg_2_pikpak_rclone(config)
        # rclone.save_self_2_config()
        # rclone.start_system_mount_service()
        rclone.run_mount()
        print("这里永远不糊执行到吧！！！！！")
    pass
    # rclone_config = get_save_json_config()
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
