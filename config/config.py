from config.read_config import get_config

mail = get_config('mail')
mail_api = mail.get("api")

requests = get_config("requests")
requests_timeout = requests.get("out_time")
requests_retry = requests.get("retry", 0)

alist = get_config("alist")
alist_domain = alist.get("domain")
alist_user = alist.get("username")
alist_pd = alist.get("password")
alist_enable = alist.get("enable", 0) == 1

def_password = get_config("def_password")

telegram_api = get_config("telegram").get("api", "")

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


def __def_captcha_callback(url: str):
    __str = input(f"请验证此url:\n{url}").split()
    return __str


__captcha_callback = __def_captcha_callback


def get_captcha_callback():
    """获取验证码获取方法

    Returns:
        _type_: _description_
    """
    return __captcha_callback


def set_captcha_callback(callback=__def_captcha_callback):
    """设置验证码获取方法

    Args:
        callback (_type_, optional): _description_. Defaults to __def_captcha_callback.
    """
    global __captcha_callback
    __captcha_callback = callback


def __def_email_verification_code_callback(mail: str):
    return input(f"请输入{mail}中获取的验证码").split()


_email_verification_code_callback = __def_email_verification_code_callback


def set_email_verification_code_callback(callback):
    """设置获取邮箱验证码回调

    Args:
        callback (function): _description_
    """
    global _email_verification_code_callback
    _email_verification_code_callback = callback


def get_email_verification_code_callback():
    """获取邮箱验证码回调

    Args:
        callback (function): _description_

    Returns:
        _type_: _description_
    """
    return _email_verification_code_callback
