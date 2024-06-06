import subprocess
import os
from pyrclone import Rclone, RcloneError, RcloneOutput
import json
from typing import Iterable, List, Optional, Tuple


cache_json_file = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "rclone.json")


class MeRclone(object):
    rclone: Rclone = Rclone()
    mount_config = []
    cache_dir = "/tmp/alist_cache"

    def __init__(self) -> None:
        try:
            with open(cache_json_file, mode="r") as file:
                self.mount_config = json.load(file)
        except:
            self.mount_config = []
            pass

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

    def save_config(self):
        with open(cache_json_file, mode='w', encoding="utf-8") as file:
            file.write(json.dumps(self.mount_config))

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

    def mount_remote(self, remote_name, path):
        if remote_name.endswith(":"):
            pass
        else:
            remote_name = remote_name + ":"
        self.rclone.command(command="mount", arguments=[
            f"{remote_name}/", path,
            f"--cache-dir={self.cache_dir}",
            "--use-mmap",
            "--umask 000",
            "--allow-non-empty",
            "--dir-cache-time 1s",
            "--vfs-cache-mode full",
            "--vfs-read-chunk-size 1M",
            "--vfs-read-chunk-size-limit 16M",
            "--checkers 4",
            "--transfers 1",
            "--vfs-cache-max-size 10G",
            # "-vv",  # 日志显示
            "--daemon",  # 后台运行
            "--allow-other",
        ])
        pass

    def get_systcemctl_all(self):
        command = ["systemctl",
                   "list-unit-files", "|", "grep", "emby"]
        result = self._execute(command)
        print(result)
    def _execute(self, command_to_run: List[str]) -> RcloneOutput:
        """_execute

        A helper function to run a given rclone command, and return the output.

        The command is expected to be given as a list of strings, ie
        the command "rclone lsd dropbox:" would be:
            ["rclone", "lsd", "dropbox:"]
        """
        self.rclone.logger.debug(f"Running: {command_to_run}")

        try:
            with subprocess.Popen(
                command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as rclone_process:
                communication_output: Tuple[bytes,
                                            bytes] = rclone_process.communicate()

                output: str = communication_output[0].decode("utf-8")
                error: str = communication_output[1].decode("utf-8")
                self.rclone.logger.debug(f"Command returned {output}")

                if error:
                    self.rclone.logger.warning(error.replace("\\n", "\n"))

                return RcloneOutput(
                    RcloneError(rclone_process.returncode),
                    output.splitlines(),
                    error.splitlines(),
                )
        except FileNotFoundError as file_missing:
            self.rclone.logger.exception(
                f"Can't find rclone executable. {file_missing}")
            return RcloneOutput(RcloneError.RCLONE_MISSING, [""], [""])
        except Exception as exception:
            self.rclone.logger.exception(
                f"Exception running {command_to_run}. Exception: {exception}"
            )
            return RcloneOutput(RcloneError.PYTHON_EXCEPTION, [""], [""])


if __name__ == "__main__":
    merclone = MeRclone()
    merclone.get_systcemctl_all()
    # merclone.update_conf_user("alist_webdav", "admin", "''''")
