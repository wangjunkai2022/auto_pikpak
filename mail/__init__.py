import logging
import os
import importlib

from dotenv import load_dotenv

# 加载.env文件中的环境变量
from .base import MailBase, SetCodeFunc, SetMailFunc
from .rapidapi import Rapidapi
from .shanyouxiang import ShanYouXiang

logger = logging.getLogger("mail")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class_names = {
    "rapidapi": Rapidapi,
    "shanyouxiang": ShanYouXiang,
    "base": MailBase,
}

# SetCodeFunc = SetCodeFunc
# SetMailFunc = SetMailFunc

def _getInstanceClass(class_name) -> MailBase:
    class_name = class_names.get(class_name)
    if class_name:
        # # 动态导入模块
        # module = importlib.import_module(module_name, package=__package__)
        # # 获取类对象
        # cls = getattr(module, class_name)
        # 创建实例
        instance: MailBase = class_name()
        return instance
    else:
        logger.debug(f"Class {class_name} not found.")
        instance: MailBase = MailBase()
        return instance


def create_one_mail(type_name=None):
    type_name = type_name or os.getenv("MAIL_TYPE")
    mail_base: MailBase = _getInstanceClass(type_name)
    logger.info(f"获取一个新邮箱中{type_name}")
    return mail_base.get_on_mail()


def get_new_mail_code(mail, type_name=None,):
    type_name = type_name or os.getenv("MAIL_TYPE")
    mail_base: MailBase = _getInstanceClass(type_name)
    logger.info(f"获取一个新邮箱中{mail}的验证码。。。。。")
    return mail_base.get_pikpak_code(mail)
