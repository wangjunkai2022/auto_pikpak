import logging

logger = logging.getLogger("mail_base")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

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


class MailBase(Singleton):
    def get_on_mail(self) -> str:
        """
        获取一个临时邮箱
        """
        logger.debug(f"{__name__} 开始获取一个临时邮箱")
        return "mail@gmail.com"
    
    def get_pikpak_code(self, mail:str) -> str:
        """
        获取pikpak最新验证码
        """
        logger.debug(f"{__name__} 获取{mail}中最新的pikpak验证码")
        return ""
        