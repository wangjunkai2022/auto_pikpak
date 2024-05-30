from pyrclone import Rclone, RcloneError
import json
from typing import Iterable, List, Optional, Tuple


class MeRclone(object):
    rclone: Rclone = Rclone()

    def __init__(self) -> None:
        # result = self.rclone.command(command="config", arguments=[
        #     "userinfo", "pikpak:", "--json"])
        # json.loads(result.output)
        # print(result)
        # result = self.rclone.command(
        #     "mount", ["pikpak:/", "/Users/evan/Desktop/pikpak"])
        # print(result)
        # info = self.__get_info("pikpak")
        # for remote in self.rclone.config.remotes:
        #     print(remote.name)
        pass

    def get_info(self, remote_name: str) -> json:
        """获取指定远程明的信息

        Args:
            remote_name (str): 需要获取的名字
        Returns:
            json: 信息
        """
        if remote_name.endswith(":"):
            pass
        else:
            remote_name = remote_name + ":"
        result = self.rclone.command(command="config", arguments=[
            "userinfo", remote_name, "--json"])
        out_str = ""
        for __str in result.output:
            out_str += __str
        json_data = json.loads(out_str)
        print(json_data)
        return json_data
    

    def update_conf_user(self, remote_name: str, user: str, password: str):
        """更新配置对应的用户名和密码

        Args:
            remote_name (str): 需要修改的库对应的名
            user (str): 用户名
            password (str): 密码
        """
        result = self.rclone.command(command="config", arguments=[
            "update", remote_name, f"user={user}", f"pass={password}"])
        print(result)


if __name__ == "__main__":
    merclone = MeRclone()
    merclone.update_conf_user("alist_webdav", "admin", "''''")
