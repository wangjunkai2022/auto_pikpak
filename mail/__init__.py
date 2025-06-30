import logging
import os
import importlib

from dotenv import load_dotenv
# 加载.env文件中的环境变量
from .base import MailBase

logger = logging.getLogger("mail")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class_names = {
    "rapidapi": ".rapidapi.Rapidapi",
    "shanyouxiang": ".shanyouxiang.ShanYouXiang"
}

def _getInstanceClass(class_name) -> MailBase:
    module_name = class_names.get(class_name)
    if module_name:
        # 动态导入模块
        module = importlib.import_module(module_name, package=__package__)
        # 获取类对象
        cls = getattr(module, class_name)
        # 创建实例
        instance: MailBase = cls()
        return instance
    else:
        logger.debug(f"Class {class_name} not found.")
        
def create_one_mail(type_name):
    type_name = type_name or os.getenv("MAIL_TYPE")
    mail_base:MailBase = _getInstanceClass(type_name)
    return mail_base.get_on_mail()

def get_new_mail_code(mail, type_name,):
    type_name = type_name or os.getenv("MAIL_TYPE")
    mail_base:MailBase = _getInstanceClass(type_name)
    return mail_base.get_pikpak_code(mail)
