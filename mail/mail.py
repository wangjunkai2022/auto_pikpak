import logging
import time
import requests
import hashlib
import random
import string
import re
import config.config as config
logger = logging.getLogger("mail")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def _get_domains():
    url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
    headers = {
        "X-RapidAPI-Key": config.mail_api,
        "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.debug(f"_get_domains 失败")
        time.sleep(2)
        return _get_domains()
    logger.debug(response.json())
    return response.json()


# 创建一个临时邮箱


def create_one_mail():
    """创建一个邮箱

    Returns:
        _type_: _description_
    """
    t = str(time.time())
    domains = _get_domains()

    while True:
        # 生成随机个字符
        random_chars_ = ''.join(random.choices(string.ascii_lowercase, k=6))
        random_chars = random_chars_ + \
            ''.join(random.choices('0123456789', k=4))
        temp_str = f"{random_chars}{domains[random.randint(0, len(domains) - 1)]}"
        # mails = get_mails(temp_str)
        # if mails.get("error"):
        #     random_chars  = ''
        # else:
        # return temp_str
        return temp_str


def get_mail():
    json_data = {
        "min_name_length": 8,
        "max_name_length": 11
    }
    url = 'https://api.internal.temp-mail.io/api/v3/email/new'
    response = requests.post(url, json=json_data,)
    response_data = response.json()
    mail = response_data['email']
    return mail


# 获取邮箱的验证码内容
def get_code(mail, max_retries=10, delay=1):
    retries = 0
    while retries < max_retries:
        url = f'https://api.internal.temp-mail.io/api/v3/email/{mail}/messages'
        response = requests.get(url,)
        html = response.json()
        if html:
            text = (html[0])['body_text']
            code = re.search('\\d{6}', text).group()
            logger.info(f'获取邮箱验证码:{code}')
            return code
        else:
            time.sleep(delay)
            retries += 1
    logger.info("获取邮箱邮件内容失败，未收到邮件...")
    return None


def get_mails(mail):
    # 创建一个md5对象
    md5 = hashlib.md5()

    # 更新md5对象的内容
    md5.update(mail.encode('utf-8'))

    # 获取MD5哈希值
    md5_hash = md5.hexdigest()
    url = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{md5_hash}/"
    headers = {
        "X-RapidAPI-Key": config.mail_api,
        "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    logger.debug(response.json())
    return response.json()


def get_new_mail_code(mail):
    """获取邮箱中最新的数字验证码

    Args:
        mail (_type_): _description_

    Returns:
        _type_: _description_
    """
    time.sleep(2)
    mails = get_mails(mail)
    code = ""
    if not isinstance(mails, list) and mails.get("error"):
        logger.debug(f"获取邮箱信息错误{mails.get('error')}")
        time.sleep(2)
        return get_new_mail_code(mail)
    if mails and len(mails) > 0:
        mail_content = mails[0]
        if mail_content:
            mail_text = mail_content.get("mail_text", "")
            temp_code_re = re.search(r"\d+", mail_text)
            if temp_code_re:
                code = temp_code_re.group()
    if code == "":
        time.sleep(2)
        return get_new_mail_code(mail)
    return code


def get_one_message(mail):
    url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/one_mail/id/%7B{mail}%7D/"
    headers = {
        "X-RapidAPI-Key": config.mail_api,
        "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    logger.debug(response.json)
    return response.json()


config.set_email_verification_code_callback(get_new_mail_code)

if __name__ == "__main__":
    # mail = create_one_mail()
    mail = "ScSDK18K@cevipsa.com"
    # mail = "qekbpt9109@amozix.com"
    logger.debug(f"{mail}")
    code = get_new_mail_code(mail)
