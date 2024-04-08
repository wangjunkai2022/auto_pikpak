import time
import requests
import hashlib
import random
import string
import re
import config


def _get_domains():
    url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
    headers = {
        "X-RapidAPI-Key": config.mail_api,
        "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"_get_domains 失败")
        time.sleep(2)
        return _get_domains()
    print(response.json())
    return response.json()


# 创建一个临时邮箱


def create_one_mail():
    t = str(time.time())
    domains = _get_domains()

    while True:
        # 生成随机个字符
        random_chars_ = ''.join(random.choices(string.ascii_lowercase, k=6))
        random_chars = random_chars_ + ''.join(random.choices('0123456789', k=4))
        temp_str = f"{random_chars}{domains[random.randint(0, len(domains) - 1)]}"
        # mails = get_mails(temp_str)
        # if mails.get("error"):
        #     random_chars  = ''
        # else:
        # return temp_str
        return temp_str


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

    print(response.json())
    return response.json()


def get_new_mail_code(mail):
    time.sleep(2)
    mails = get_mails(mail)
    code = ""
    if not isinstance(mails, list) and mails.get("error"):
        print(f"获取邮箱信息错误{mails.get('error')}")
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
    print(response.json)
    return response.json()


if __name__ == "__main__":
    # mail = create_one_mail()
    mail = "ScSDK18K@cevipsa.com"
    # mail = "qekbpt9109@amozix.com"
    print(f"{mail}")
    code = get_new_mail_code(mail)
