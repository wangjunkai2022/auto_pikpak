import os
from .rapidapi import (
    create_one_mail as rapidapi_get_mail,
    get_new_mail_code as rapidapi_get_new_mail_code,
)

from .shanyouxiang import get_one_mail, get_pikpak_code


def create_one_mail():
    # return rapidapi_get_mail()
    SHANYOUXIANG_KEY = os.getenv("SHANYOUXIANG_KEY")
    return get_one_mail(SHANYOUXIANG_KEY)


def get_new_mail_code(mail):
    # return rapidapi_get_new_mail_code(mail)
    return get_pikpak_code(mail)
