from dataclasses import dataclass
import enum
import logging
import subprocess
from typing import Iterable, List, Tuple
logger = logging.getLogger("system_service")


class SystemServiceTager(enum):
    all = 1
    alist = 2
    rclone = 3
    emby = 4


@dataclass
class SystemServiceOutput:
    output: List[str]
    error: List[str]


class SystemService:
    # tager: SystemServiceTager
    server_name: Iterable[str] = ["alist.service",
                                  "rclone.service", "emby-server.service"]

    def __init__(self, tager: SystemServiceTager = SystemServiceTager.all) -> None:
        if tager == SystemServiceTager.all:
            pass
        elif tager == SystemServiceTager.alist:
            self.server_name = ["alist.service"]
        elif tager == SystemServiceTager.rclone:
            self.server_name = ["rclone.service"]
        elif tager == SystemServiceTager.emby:
            self.server_name = ["emby-server.service"]

    def run(self):
        self._run_command("start", self.server_name)

    def stop(self):
        self._run_command("stop", self.server_name)

    def status(self):
        self._run_command("status", self.server_name)

    def _run_command(
        self, command: str, arguments: Iterable[str] = tuple()
    ) -> SystemServiceOutput:
        full_command: List[str] = ["systemctl", command]
        full_command += arguments

        return self._execute(full_command)

    def _execute(self, command_to_run: List[str]) -> SystemServiceOutput:
        logger.debug(f"Running: {command_to_run}")
        try:
            with subprocess.Popen(
                command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as rclone_process:
                communication_output: Tuple[bytes,
                                            bytes] = rclone_process.communicate()

                output: str = communication_output[0].decode("utf-8")
                error: str = communication_output[1].decode("utf-8")
                logger.debug(f"Command returned {output}")

                if error:
                    logger.warning(error.replace("\\n", "\n"))

                return SystemServiceOutput(
                    output.splitlines(),
                    error.splitlines(),
                )
        except FileNotFoundError as file_missing:
            logger.exception(
                f"Can't find rclone executable. {file_missing}")
            return SystemServiceOutput([""], [""])
        except Exception as exception:
            logger.exception(
                f"Exception running {command_to_run}. Exception: {exception}"
            )
            return SystemServiceOutput([""], [""])


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    output = SystemService().status()
    print(output)
