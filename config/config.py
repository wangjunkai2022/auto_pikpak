import os
from config.read_config import get_config

# mail_api = get_config('mail').get("api")
# twocapctha_api = get_config('twocaptcha').get("api")
# shanyouxiang_api = get_config("shanyouxiang").get("api") or ""

change_model = get_config("invate_change_model") or "none"
requests = get_config("requests")
requests_timeout = requests.get("out_time")
requests_retry = requests.get("retry", 0)

mail_type = get_config("mail_type")
os.environ['MAIL_TYPE'] = mail_type

alist = get_config("alist")
alist_domain = alist.get("domain")
alist_user = alist.get("username")
alist_pd = alist.get("password")
alist_enable = alist.get("enable", 0) == 1

def_password = get_config("def_password")

rclone = get_config("rclone")
rclone_mount = rclone.get("mount_root")

__log = print


def get_log():
    """获取日志显示方法

    Returns:
        _type_: _description_
    """
    return __log


def set_log(callback=print):
    """设置日子显示方法

    Args:
        callback (_type_, optional): _description_. Defaults to print.
    """
    global __log
    __log = callback