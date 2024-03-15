import platform

from enum import Enum


class sys_enum(Enum):
    windows = 1,
    linux = 2,
    macos = 3,
    other = 4,


def get_platform():
    sys_platform = platform.platform().lower()
    _sys = sys_enum.other
    if "windows" in sys_platform:
        _sys = sys_enum.windows
        print("Windows")
    elif "macos" in sys_platform:
        _sys = sys_enum.macos
        print("Mac os")
    elif "linux" in sys_platform:
        print("Linux")
        _sys = sys_enum.linux
    else:
        _sys = sys_enum.other
        print("其他系统")


if __name__ == "__main__":
    get_platform()
