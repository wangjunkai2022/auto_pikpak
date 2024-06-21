from captcha.chmod import open_url2token
from mail.mail import get_new_mail_code

from config import config


def set_def_callback():
    config.set_captcha_callback(open_url2token)
    config.set_email_verification_code_callback(get_new_mail_code)
