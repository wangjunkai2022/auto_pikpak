import datetime
import json
import os
import random
import string
import threading
from typing import List

import schedule

import config.config as config
import alist.alist as alist
from mail import create_one_mail, get_new_mail_code
import time
import logging
from pikpak.pikpak_super import HandleSuper, PikPakSuper
from proxy_ip import pop_prxy_pikpak
from rclone import PikPakJsonData, PikPakRclone, RCloneManager
from tools import set_def_callback
from proxy_ip import main_th_proxy
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class BasePikpakData(PikPakSuper):
    name = None
    disabled = False

    def __init__(self, mail: str = None, pd: str = None, name=None, disabled: bool = False):
        super().__init__(mail, pd)
        self.name = name
        self.disabled = disabled


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


class ManagerPikPak(Singleton):

    opation_index: int = -1
    pikpak_go_list: List[BasePikpakData] = []

    def __init__(self) -> None:
        self.opation_index = 0

    def change_opation_2(self, pikpak_data: BasePikpakData):
        """
        替换操作的pikpak为次pikpak
        """
        try:
            self.opation_index = self.pikpak_go_list.index(pikpak_data)
        except:
            for pikpak in self.pikpak_go_list:
                if pikpak.name == pikpak_data.name:
                    self.opation_index = self.pikpak_go_list.index(pikpak)
                    break

    def change_opation_storage_name_2(self, storage_name: str):
        """
        替换操作的pikpak为此名字的存储
        """
        for pikpak in self.pikpak_go_list:
            if pikpak.name == storage_name:
                self.opation_index = self.pikpak_go_list.index(pikpak)
                return
        raise Exception(f"替换操作的pikpak:{storage_name}失败")


class ManagerAlistPikpak(ManagerPikPak, alist.Alist):

    def __init__(self):
        alist.Alist.__init__(self)
        self.saveToNowConif()
        for pikpak_data in self.get_all_pikpak_storage():
            # if not pikpak_data.get("disabled"):
            pikpak_go = BasePikpakData(
                mail=pikpak_data.get("username"),
                pd=pikpak_data.get("password"),
                name=pikpak_data.get("name"),
                disabled=pikpak_data.get("disabled"),
            )
            self.pikpak_go_list.append(pikpak_go)
        self.opation_index = 0

    # 直接pop一个Alsit中的一个pikpak登陆
    def get_opation_pikpak(self) -> BasePikpakData:
        return self.pikpak_go_list[self.opation_index]

    def update_opation_pikpak_go(self, pikpak_go: BasePikpakData):
        alist_storage = None
        for data in self.get_storage_list().get('content'):
            if data.get("mount_path")[1:] == self.get_opation_pikpak().name:
                alist_storage = data
                break
        remark_str = alist_storage.get("remark")
        if remark_str == "":
            remark_str = '{}'
        remark_json = json.loads(remark_str,)
        share = remark_json.get("share")
        if share:
            # 拥有分享地址 直接分享
            pass
        else:
            # 没有分享地址 开始分享opatins Pikpak
            share = self.get_opation_pikpak().start_share_self_files()
        remark_json["share"] = share
        share_task = pikpak_go.save_share(share.get("share_id"))
        time.sleep(10)  # 等待10秒保证分享保存成功
        addition = json.loads(alist_storage.get("addition"))
        old_username = addition.get('username')
        old_password = addition.get('password')
        pikpak_user = remark_json.get("pikpak_user")
        if not old_username and pikpak_user:
            old_username = pikpak_user.get('username')
            old_password = pikpak_user.get('password')
        logger.info(
            f"更新Alist中的pikpak\npath:{self.get_opation_pikpak().name}\n原账户:{old_username}\n原密码{old_password}")
        addition["username"] = pikpak_go.mail
        addition["password"] = pikpak_go.pd
        addition['refresh_token'] = pikpak_go.refresh_token
        addition['platform'] = "web"
        remark_json['pikpak_user'] = {
            'username': pikpak_go.mail,
            'password': pikpak_go.pd,
        }
        alist_storage["addition"] = json.dumps(addition)
        alist_storage['remark'] = json.dumps(
            remark_json, ensure_ascii=False, indent=4)
        logger.debug(alist_storage)
        self.update_storage(alist_storage)


class ManagerRclonePikpak(ManagerPikPak, RCloneManager):
    pass
    # def __init__(self) -> None:
    #     ManagerPikPak.__init__(self)
    #     RCloneManager.__init__(self)
    #     pass

    # def pop_not_vip_pikpak(self) -> BasePikpakData:
    #     self.opation_pikpak_go = None
    #     ManagerPikPak.pop_not_vip_pikpak(self)
    #     if self.opation_index >= len(self.json_config):
    #         return None
    #     pikpak_rclone: PikPakRclone = self.conifg_2_pikpak_rclone(
    #         self.json_config[self.opation_index])
    #     # 尝试直接重rclone获取pikpak的vip状态
    #     rclone_service_info = pikpak_rclone.get_info()
    #     if rclone_service_info:
    #         if rclone_service_info.get("VIPType") == "novip":
    #             self.opation_pikpak_go = BasePikpakData(
    #                 pikpak_rclone.user, pikpak_rclone.password, name=pikpak_rclone.remote)
    #     else:
    #         opation_pikpak_go = BasePikpakData(
    #             mail=pikpak_rclone.user, pd=pikpak_rclone.password, name=pikpak_rclone.remote)
    #         if opation_pikpak_go.get_vip_day_time_left() <= 0:
    #             self.opation_pikpak_go = opation_pikpak_go
    #     if self.opation_pikpak_go:
    #         return self.opation_pikpak_go
    #     else:
    #         return self.pop_not_vip_pikpak()

    # def save_pikpak_2(self, pikpak_go: BasePikpakData):
    #     if self.opation_pikpak_go.mail == pikpak_go.mail:
    #         logger.info(f"保存pikpak rclone中的账户和现在的账户时同一个这里不做修改")
    #         return

    #     data = self.conifg_2_pikpak_rclone[self.opation_index]
    #     data["pikpak_user"] = pikpak_go.mail
    #     data["pikpak_password"] = pikpak_go.pd
    #     logger.debug(self.conifg_2_pikpak_rclone)
    #     self.save_config()


def radom_password():
    chars = string.ascii_letters+string.digits
    # 得出的结果中字符会有重复的
    return ''.join([random.choice(chars) for i in range(random.randint(8, 11))])


def get_proxy():
    logger.info("获取代理地址中。。。。。")
    ip, proxy_type = pop_prxy_pikpak()
    logger.info(f"获取到的代理:{ip}")
    return ip, proxy_type


def pikpakdata_2_pikpakdata(old_pikpak: BasePikpakData, new_pikpak: BasePikpakData):
    """
    旧账户的资源复制到新账户中
    """
    if new_pikpak.get_vip_day_time_left() > 0:
        share = old_pikpak.start_share_self_files()
        logger.info(
            f"分享原账户:\nemail: {old_pikpak.mail}\npd: {old_pikpak.pd}\n分享代码是: {share}")
        time.sleep(10)
        share_id = share.get("share_id", None)
        if not share_id:
            raise Exception("分享错误")
        new_pikpak.save_share(share_id)
        logger.info(f"保存原账户的资源到新账户:\n{new_pikpak.mail}\n{new_pikpak.pd}")
    else:
        raise Exception("新账户没有vip")


def change_all_pikpak():
    """
    注册新的pikpak替换原来的pikpak
    """
    alistPikpak: ManagerPikPak = ManagerAlistPikpak()
    for pikpak_go in alistPikpak.pikpak_go_list:
        if pikpak_go.disabled:
            continue
        error = None
        pikpak: BasePikpakData = None
        for count in range(3):
            try:
                if not pikpak:
                    handler = HandleSuper(
                        get_token=config.get_captcha_callback(),
                        get_mailcode=config.get_email_verification_code_callback(),
                        email_address=create_one_mail,
                        get_password=radom_password,
                        get_proxy=get_proxy,
                    )
                    pikpak = BasePikpakData.create(handler)
                else:
                    logger.info("pikpak 已经注册成功 但是后续报错 这里继续使用pikpak")
                time.sleep(60)
                pikpak.try_get_vip()
                # pikpakdata_2_pikpakdata(pikpak_go, pikpak)
                alistPikpak.change_opation_2(pikpak_go)
                alistPikpak.update_opation_pikpak_go(pikpak)
                logger.info(f"替换原账户的alit或者rclone中")
                pikpak = None
                error = None
                break
            except Exception as e:
                error = e
        if error:
            raise error

    logger.info('注册新的pikpak替换原来的pikpak over')


def check_all_pikpak_vip():
    """运行所有的pikpak账户检测
    """
    logger.info("开始执行系统中的会员状态检测")
    alistPikpak: ManagerPikPak = ManagerAlistPikpak()
    for pikpak_go in alistPikpak.pikpak_go_list:
        logger.info(f"正在整理的pikpak\n {pikpak_go.mail}")
        pikpak_go.set_proxy(get_proxy())
        if pikpak_go.try_get_vip():
            vip_day = pikpak_go.get_vip_day_time_left()
            logger.info(f"尝试获取vip成功 当前vip剩余天数{vip_day}")
            continue
        handler = HandleSuper(
            get_token=config.get_captcha_callback(),
            get_mailcode=config.get_email_verification_code_callback(),
            email_address=create_one_mail,
            get_password=radom_password,
            get_proxy=get_proxy,
        )
        pikpak: BasePikpakData = BasePikpakData.create(handler)
        time.sleep(60)
        pikpak.try_get_vip()
        # pikpakdata_2_pikpakdata(pikpak_go, pikpak)
        alistPikpak.change_opation_2(pikpak_go)
        alistPikpak.update_opation_pikpak_go(pikpak)
        logger.info(f"替换原账户的alit或者rclone中")

    logger.info("Over")

def is_today_one(timestamp):
  """
  判断时间与现在是否跨1天

  Args:
    timestamp: 时间戳 (秒).

  Returns:
    True 如果时间戳是，False 如果不是。
  """

  dt_obj = datetime.datetime.fromtimestamp(timestamp)
  today_date = datetime.datetime.now().date()
  day = dt_obj.date() - today_date
  return day.days >= -5

def 替换Alist储存库(email, pd, name):
    pikpak = BasePikpakData(email, pd, name)
    if pikpak.try_get_vip():
        alist = ManagerAlistPikpak()
        alist.change_opation_storage_name_2(name)
        alist.update_opation_pikpak_go(pikpak)
    else:
        raise Exception("传入的账户没有vip")


def 刷新PikPakToken(alist_storage):
    name = alist_storage.get('name')
    logger.info(f"开始刷新{name}的pikpak_token")
    alist = ManagerAlistPikpak()
    storage_data = next(x for x in alist.get_storage_list().get(
        'content') if x.get("mount_path")[1:] == name)
    pikpak = next(x for x in alist.pikpak_go_list if x.name == name)
    pikpak.login_out()
    pikpak.login()
    addition = json.loads(storage_data.get("addition"))
    old_token = addition.get('refresh_token')
    logger.debug(f"pikpak原token:{old_token}")
    logger.debug(f"pikpak新token:{pikpak.refresh_token}")
    addition['refresh_token'] = pikpak.refresh_token
    storage_data["addition"] = json.dumps(addition)
    logger.debug(storage_data)
    alist.update_storage(storage_data)


def 所有Alist的储存库() -> List[BasePikpakData]:
    logger.info("开始获取本地所有的配置")
    base_pikpak: ManagerPikPak = ManagerAlistPikpak()
    return base_pikpak.get_all_pikpak_storage()


def 激活存储库vip(alist_storage) -> BasePikpakData:
    base_pikpak: ManagerPikPak = ManagerAlistPikpak()
    base_pikpak.change_opation_storage_name_2(alist_storage.get('name'))
    pikpak_ = base_pikpak.get_opation_pikpak()
    # pikpak_.login()
    # pikpak_.set_proxy(get_proxy())
    try:
        if pikpak_.try_get_vip():
            return pikpak_
    except Exception as e:
        if str(e).startswith("网络连接错误"):
            logger.error("网络连接错误 重新获取新代理")
            pikpak_.set_proxy(get_proxy())
            pikpak_.save_self()
            激活存储库vip(alist_storage)
        else:
            raise e
    return 注册新号激活AlistStorage(alist_storage)


def 注册新号激活AlistStorage(alist_storage) -> BasePikpakData:
    mail = alist_storage.get('name')

    logger.info(f"正在整理的存储\n {mail}")
    pikpak = 注册新号激活_Pikpsk(mail)
    ManagerAlistPikpak().change_opation_storage_name_2(alist_storage.get('name'))
    ManagerAlistPikpak().update_opation_pikpak_go(pikpak)
    logger.info(f"替换原账户的alit或者rclone中")
    return pikpak


def 注册新号激活_Pikpsk(mail: str = ""):
    logger.info(f"给帐号 {mail} 注册新号并填写他的邀请码")
    pikpak: BasePikpakData = BasePikpakData(mail)
    pikpak.login()
    invite_code = pikpak.get_self_invite_code()
    logger.info(f"帐号 {mail} 邀请码是{invite_code}")
    pikpak = 注册并填写邀请(invite_code)
    vip_day = pikpak.get_vip_day_time_left()
    logger.info(f"新帐号 {pikpak.mail} Vip 信息是：{vip_day}")
    return pikpak


def copye_list_2_rclone_config():
    """复制alist的配置到rclone的配置json配置中
    """
    alist_server = alist.Alist()
    rclone_manager = ManagerRclonePikpak()
    # alist_server.saveToNowConif()
    rclone_configs: List[PikPakJsonData] = []
    for _alist in alist_server.get_storage_list()["content"]:
        if _alist.get("driver") == "PikPak":
            alist_mount_path = _alist.get("mount_path")[1:]
            addition = json.loads(_alist.get("addition"))
            rclone_json_data = PikPakJsonData({
                "remote": "pikpak_" + alist_mount_path,
                "pikpak_user": addition.get("username"),
                "pikpak_password": addition.get("password"),
                "mout_path": os.path.join(config.rclone_mount, alist_mount_path)
            })
            rclone_configs.append(rclone_json_data)
    logger.debug(rclone_configs)
    rclone_manager.json_config = rclone_configs
    rclone_manager.save_config()


def 注册并填写邀请(邀请码: str = ""):
    if not 邀请码 or 邀请码 == "":
        logger.error("邀请码不正确")
    logger.error(f"注册并邀请中{邀请码}")
    handler = HandleSuper(
        get_token=config.get_captcha_callback(),
        get_mailcode=config.get_email_verification_code_callback(),
        email_address=create_one_mail,
        get_password=radom_password,
        get_proxy=get_proxy,
    )
    pikpak: BasePikpakData = BasePikpakData.create(handler)
    time.sleep(10)
    PikPakMail填写邀请码(pikpak.mail, 邀请码)
    return pikpak

def 运行某个Pikpak模拟人操作(mail, auto_proxy=True)->BasePikpakData:
    logger.info(f"运行:{mail} Pikpak模拟人操作")
    pikpak: BasePikpakData = BasePikpakData(mail)
    pikpak.is_auto_login = True
    try:
        pikpak.read_self()
        if not pikpak.proxies or not pikpak.proxies.get("http") or pikpak.proxies.get("http") == "":
            proxy = get_proxy()
            pikpak.set_proxy(*proxy)
            pikpak.save_self()
        pikpak.run_test()
        vip_day = pikpak.get_vip_day_time_left()
        if vip_day > 0:
            logger.log(f"注意：：：：：帐号{mail}现在是vip哦")
    except Exception as e:
        if str(e).startswith("网络连接错误") and auto_proxy:
            proxy = get_proxy()
            pikpak.set_proxy(*proxy)
            pikpak.save_self()
            return 运行某个Pikpak模拟人操作(mail, auto_proxy)
        raise e
    logger.info(f"运行:{mail} Pikpak模拟人操作  完成---------")
    return pikpak

def PikPakMail填写邀请码(mail, 邀请码):
    pikpak: BasePikpakData = 运行某个Pikpak模拟人操作(mail, False)
    pikpak.set_activation_code(邀请码)

def PiaPak保活():
    logger.info(f"开始运行所有帐号模拟人为操作")
    json_datas = BasePikpakData("").read_all_json_data()
    for mail in json_datas.keys():
        temp_json = json_datas.get(mail)
        if temp_json.get("create_time") and is_today_one(temp_json.get("create_time")):
            threading.Thread(target=运行某个Pikpak模拟人操作,args=(mail, True)).start()

def test():
    for index in range(2):
        threading.Thread(target=get_proxy).start()

def main():
    # change_all_pikpak()
    # 注册并填写邀请("92196679")
    # PikPakMail填写邀请码("gibtukcmnm2687@hotmail.com","33450720")
    # 运行某个Pikpak模拟人操作("atnzlp9830@tgvis.com")
    # threading.Thread(target=注册新号激活_Pikpsk,args=("gibtukcmnm2687@hotmail.com",)).start()
    # threading.Thread(target=test).start()
    threading.Thread(target=PiaPak保活).start()
    # threading.Thread(target=运行某个Pikpak模拟人操作,args=("fldgevng827@hotmail.com",)).start()
    pass

schedule.every().day.at("08:30").do(PiaPak保活)
schedule.every(1).second.do(main_th_proxy)
# 3小时执行一次看看
schedule.every(1).hour.do(PiaPak保活) 
if __name__ == "__main__":
    set_def_callback()
    # 其他程序代码可以放在这里
    # 主线程会持续运行，不会被调度器阻塞
    threading.Thread(target=main).start()

while True:
    # print("Main thread is running...")
    # schedule.run_pending()
    schedule.run_pending()
    time.sleep(1)
