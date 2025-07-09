import logging
import re
from types import FunctionType

logger = logging.getLogger("mail")
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger.addHandler(handler)


def _mail_func(tips: str = "请输入邮箱\n"):
    return input(tips)


def _code_func(mail: str):
    return input(f"请输入{mail}中获取到的验证码")


class CallbackData():
    get_mail_callback = None
    get_code_callback = None
    def __init__(self):
        self.get_mail_callback = _mail_func
        self.get_code_callback = _code_func

callbackData = CallbackData()

def SetMailFunc(func):
    if func and isinstance(func, FunctionType):
        callbackData.get_mail_callback = func
    else:
        callbackData.get_mail_callback = _mail_func


def SetCodeFunc(func):
    if func and isinstance(func, FunctionType):
        callbackData.get_code_callback = func
    else:
        callbackData.get_code_callback = _code_func


class SingletonMeta(type):
    """自定义元类，用于创建单例类"""

    _instances = {}  # 用于存储每个类的单例实例

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """单例基类，使用 SingletonMeta 元类"""

    pass


def _is_valid_email(email):
    # 正则表达式用于匹配邮箱格式
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return True
    else:
        return False


class MailBase(Singleton):
    def get_on_mail(self) -> str:
        """
        获取一个临时邮箱
        """
        logger.debug(f"{__name__} 开始获取一个临时邮箱")
        if self.__class__ == MailBase:
            pass
        else:
            return "mail@mail.mail"
        mail = callbackData.get_mail_callback().strip()
        if _is_valid_email(mail):
            logger.debug(f"输入邮箱是:\n{mail}")
            return mail
        else:
            logger.error(f"输入的邮箱有误:\n{mail}")
            return self.get_on_mail()

    def get_pikpak_code(self, mail: str) -> str:
        """
        获取pikpak最新验证码
        """
        logger.debug(f"{__name__} 获取{mail}中最新的pikpak验证码")
        if self.__class__ == MailBase:
            pass
        else:
            return "123456"
        code = callbackData.get_code_callback(f"请输入邮箱{mail}中获得的Pikpak验证码\n").strip()
        if code:
            logger.debug(f"输入Code是:\n{code}")
            return code
        else:
            logger.error(f"{mail}输入的code有误:\n{code}")
            return self.get_pikpak_code(mail)
