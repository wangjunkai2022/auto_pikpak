from datetime import datetime
import imaplib
import email
import json
import logging
import os
import re
from time import sleep
import requests
from dotenv import load_dotenv
# 加载.env文件中的环境变量
load_dotenv()

logger = logging.getLogger("mail_shanyouxiang")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# IMAP 服务器信息
IMAP_SERVER = "imap.shanyouxiang.com"
IMAP_PORT = 993  # IMAP SSL 端口

# 邮件发送者列表（用于查找验证码）
VERIFICATION_SENDERS = ["noreply@accounts.mypikpak.com"]


def _get_pikpak_codes(email_user, email_password):
    folders = ["INBOX", "Junk"]
    mails = []
    try:
        # 连接 IMAP 服务器
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email_user, email_password)  # 直接使用邮箱密码登录
        for folder in folders:
            # 选择文件夹
            status, _ = mail.select(folder)
            if status != "OK":
                return {"code": 0, "msg": f"无法访问 {folder} 文件夹"}

            # 搜索邮件
            status, messages = mail.search(None, "ALL")
            if status != "OK" or not messages[0]:
                return {"code": 0, "msg": f"{folder} 文件夹为空"}

            message_ids = messages[0].split()

            for msg_id in message_ids[::-1]:  # 从最新邮件开始查找
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        from_email = msg["From"]

                        if any(sender in from_email for sender in VERIFICATION_SENDERS):
                            timestamp_str = msg["Date"]

                            # 解析邮件正文
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/html":
                                        body = part.get_payload(decode=True).decode(
                                            "utf-8"
                                        )
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode("utf-8")

                            # 提取验证码
                            match = re.search(r"\b(\d{6})\b", body)
                            if match:
                                verification_code = match.group(1)
                                # 将字符串转换为 datetime 对象
                                dt = datetime.strptime(
                                    timestamp_str, "%a, %d %b %Y %H:%M:%S %z"
                                )

                                # 转换为时间戳（秒）
                                timestamp = dt.timestamp()
                                verification_data = {
                                    "data": timestamp_str,
                                    "code": verification_code,
                                    "timestamp": timestamp,
                                }
                                mails.append(verification_data)
                                break

        mail.logout()
        logger.debug(f"当前获取到的pikpak的邮箱的信息：{mails}")
        list.sort(mails, key=lambda x: x.get("timestamp"), reverse=True)
        return mails
    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP 认证失败: {e}")
    except Exception as e:
        logger.error(f"IMAP 发生错误: {e}")
    logger.error(f"没有找到pikpak对应的邮件 等待60秒后再次查找")
    return _get_pikpak_codes(email_user, email_password)


base_url = "https://zizhu.shanyouxiang.com"
mails_file = "shanyouxiang.json"


def read_json_file() -> dict:
    """
    读取指定的 JSON 文件，若文件不存在则返回空的 JSON 数据。

    :param filename: JSON 文件名（不包含路径）
    :return: 从文件读取的 JSON 数据或空字典
    """
    if not mails_file.endswith(".json"):
        raise ValueError("Filename must end with '.json'")

    # 检查文件是否存在
    if os.path.exists(mails_file):
        with open(mails_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data  # 返回读取的数据
            except json.JSONDecodeError:
                print(f"Error decoding JSON from the file: {mails_file}")
                return {}
    else:
        return {}  # 返回空的 JSON 数据


def update_json_file(new_data):
    """
    更新指定的 JSON 文件，将相同 key 的内容更新为新数据。

    :param filename: JSON 文件名（不包含路径）
    :param new_data: 要更新的 JSON 数据（字典形式）
    """
    if not mails_file.endswith(".json"):
        raise ValueError("Filename must end with '.json'")

    # 先读取已有的数据
    existing_data = read_json_file()
    old_data = existing_data.get(new_data.get("mail"))
    if old_data:
        logger.info(f"更新已存在数据 {old_data}")
    existing_data[new_data.get("mail")] = new_data

    # 写回到文件
    with open(mails_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)


def get_one_mail(key: str = "这里输入闪邮箱的邮箱密钥"):
    logger.info("开始获取一个新邮箱")
    response = requests.get(f"{base_url}/kucun")
    json_data = response.json()
    logger.debug(f"查询系统剩余接口数据：{json_data}")
    num_count = requests.get(f"{base_url}/yue?card={key}").json().get("num")
    logger.debug(f"卡剩余可用邮箱数量:{num_count}")
    mail_type = ""
    if num_count and num_count > 0:
        if json_data.get("hotmail") > 0:
            mail_type = "hotmail"
        elif json_data.get("outlook") > 0:
            mail_type = "outlook"
    else:
        logger.error("当前卡密剩余数量是0")
    if mail_type != "":
        try:
            response = requests.get(
                f"{base_url}/huoqu?card={key}&shuliang={1}&leixing={mail_type}"
            )
            text = response.text
            # text = "gibtukcmnm2687@hotmail.com----SafocDVpQK----M.C540_BAY.0.U.-ChA7k!LEZ5q3pIsxgdukypa0flsv3Ufyeq6t!hLz6SsxT9cvD6BYHbhNUd2khc*DHfJgHSrTglzeww7DTzPIz2piqI2jDTE4vaQxZRxVHV8*xjNcauQ6H4loQJ1CQZsUlouI0B1jrqQiEUy1Uju9sLzmsVynnS29nCV9C0aMpmgN6DNFxqORf2dcFC083ckdTMQVN3L973xkNAYrqI6ZjvEXQVWzXTRUTrEsN2cZ9HyNzZIElaKdtfoGIrCLluQUrDirmBzBq5cBqbjtqObLuDrzekFhxhzD18IXdr6agqHwZl3LRSahx6igmoXSIs1Xd5expQ8LY6qTlS!bfD9FSkpp93ueA9IDEx9J7pH6e6GiXk8S2dkSg8!!Zn9D4PnIFCCDI2Ureg74Huq*9Hab320$----8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2"
            text = text.strip()
            datas = text.split("----")
            json_data = {
                "all_text": text,
                "mail": datas[0],
                "password": datas[1],
                "token": datas[2],
                "uuid": datas[3],
            }
            logger.debug(f"获取邮箱返回数据：{json_data}")
            update_json_file(json_data)
            return datas[0]
        except Exception as e:
            logger.error(f"获取邮箱失败：{e}")
    else:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"{time_str} 闪邮箱现在库存是0")

    sleep(60)
    return get_one_mail(key)


def get_pikpak_code(mail: str = ""):
    logger.info(
        f"开始获取验证码:{mail} 担心没有收到验证码 所以这里等待一分钟 以保证正常发送了邀请码"
    )
    sleep(60)
    password = read_json_file().get(mail).get("password")
    if password:
        codes = _get_pikpak_codes(mail, password)
        return codes[0].get("code")


if __name__ == "__main__":
    SHANYOUXIANG_KEY = os.getenv("SHANYOUXIANG_KEY")
    mail = get_one_mail(SHANYOUXIANG_KEY)
    if mail:
        code = get_pikpak_code(mail)
        print(code)
