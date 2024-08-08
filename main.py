import json
import os
import random
import string
from typing import List
from pikpak import PikPak, crete_invite, run_new_test
from captcha.chmod import open_url2token
import config.config as config
import asyncio
import alist.alist as alist
from mail.mail import create_one_mail, get_new_mail_code
import time
import logging
from pikpak.pikpak_super import HandleSuper, PikPakSuper
from proxy_ip import pop_prxy_pikpak
from rclone import PikPakJsonData, PikPakRclone, RCloneManager
import telegram
from tools import set_def_callback
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_start_share_id(pikpak: PikPak = None):
    try:
        pikpak_api = pikpak.pikpakapi
        # 创建一个事件循环thread_loop
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        main_loop = asyncio.get_event_loop()
        get_future = asyncio.ensure_future(pikpak_api.login())
        main_loop.run_until_complete(get_future)
        # 获取Pack From Shared的id
        get_future = asyncio.ensure_future(
            pikpak_api.path_to_id("Pack From Shared"))
        main_loop.run_until_complete(get_future)
        result = get_future.result()
        if len(result) == 1:
            id_Pack_From_Shared = result[-1].get("id")
            # 获取Pack From Shared文件夹下的所有文件夹
            get_future = asyncio.ensure_future(
                pikpak_api.file_list(parent_id=id_Pack_From_Shared))
            main_loop.run_until_complete(get_future)
            result = get_future.result()
            if len(result.get("files")) <= 0:
                id_Pack_From_Shared = None
        else:
            id_Pack_From_Shared = None

        # 获取Pack From Shared文件夹下的所有文件夹
        get_future = asyncio.ensure_future(
            pikpak_api.file_list(parent_id=id_Pack_From_Shared))
        main_loop.run_until_complete(get_future)
        result = get_future.result()

        # 需要分享的文件夹id
        fils_id = []
        for file in result.get("files"):
            if file.get("name") == 'My Pack' or file.get("name") == 'Pack From Shared':
                pass
            else:
                fils_id.append(file.get("id"))
        # for file in invite.get("share", []):
        #     get_future = asyncio.ensure_future(pikpak_api.path_to_id(file))
        #     main_loop.run_until_complete(get_future)
        #     result = get_future.result()
        #     fils_id.append(result[-1].get("id"))
        get_future = asyncio.ensure_future(
            pikpak_api.file_batch_share(fils_id, expiration_days=7)
        )
        main_loop.run_until_complete(get_future)
        result = get_future.result()
        logger.debug(result)
        return result.get("share_id", None)
    except:
        logger.error("分享失败 重新分享")
        time.sleep(30)
        return get_start_share_id(pikpak)


class BasePikpakData(PikPakSuper):
    name = None

    def __init__(self, mail: str = None, pd: str = None, name=None):
        super().__init__(mail, pd)
        self.name = name


class ManagerPikPak:
    opation_pikpak_go: BasePikpakData = None
    opation_index: int = -1

    def __init__(self) -> None:
        self.opation_index = -1

    def pop_not_vip_pikpak(self) -> BasePikpakData:
        self.opation_index += 1

    def save_pikpak_2(self, pikpak_go: BasePikpakData):
        pass

    def get_all_not_vip(self) -> List[BasePikpakData]:
        """获取所有不是会员的Pikpak

        Returns:
            List[PikPak]: _description_
        """
        not_vip_list: List[BasePikpakData] = []
        while True:
            not_vip = self.pop_not_vip_pikpak()
            if not_vip:
                not_vip_list.append(not_vip)
            else:
                break
        return not_vip_list


class ManagerAlistPikpak(ManagerPikPak, alist.Alist):
    pikpak_user_list: List[dict] = None

    def __init__(self):
        alist.Alist.__init__(self)
        self.saveToNowConif()
        self.pikpak_user_list = self.get_all_pikpak_storage()

    # 直接pop一个Alsit中的一个Vip的剩余天数小于0的pikpak登陆
    def pop_not_vip_pikpak(self) -> BasePikpakData:
        if len(self.pikpak_user_list) <= 0 or self.opation_index >= len(self.pikpak_user_list) - 1:
            return None
        self.opation_index = self.opation_index + 1
        if self.get_opation_pikpak().get_vip_day_time_left() <= 0:
            return self.opation_pikpak_go
        else:
            return self.pop_not_vip_pikpak()

    # 直接pop一个Alsit中的一个pikpak登陆
    def get_opation_pikpak(self) -> BasePikpakData:
        pikpak_data = self.pikpak_user_list[self.opation_index]
        if not self.opation_pikpak_go or self.opation_pikpak_go.mail != pikpak_data.get("username") or self.opation_pikpak_go.pd != pikpak_data.get("password") or self.opation_pikpak_go.name != pikpak_data.get("name"):
            self.opation_pikpak_go = BasePikpakData(
                mail=pikpak_data.get("username"),
                pd=pikpak_data.get("password"),
                name=pikpak_data.get("name")
            )
        return self.opation_pikpak_go

    def save_pikpak_2(self, pikpak_go: BasePikpakData):
        storage_list = self.get_storage_list()
        for data in storage_list.get("content"):
            addition = json.loads(data.get("addition"))
            if addition.get("username") == self.opation_pikpak_go.mail:
                addition["username"] = pikpak_go.mail
                addition["password"] = pikpak_go.pd
                data["addition"] = json.dumps(addition)
                logger.debug(data)
                self.update_storage(data)
            logger.debug(addition)


class ManagerRclonePikpak(ManagerPikPak, RCloneManager):

    def __init__(self) -> None:
        ManagerPikPak.__init__(self)
        RCloneManager.__init__(self)
        pass

    def pop_not_vip_pikpak(self) -> BasePikpakData:
        self.opation_pikpak_go = None
        ManagerPikPak.pop_not_vip_pikpak(self)
        if self.opation_index >= len(self.json_config):
            return None
        pikpak_rclone: PikPakRclone = self.conifg_2_pikpak_rclone(
            self.json_config[self.opation_index])
        # 尝试直接重rclone获取pikpak的vip状态
        rclone_service_info = pikpak_rclone.get_info()
        if rclone_service_info:
            if rclone_service_info.get("VIPType") == "novip":
                self.opation_pikpak_go = BasePikpakData(
                    pikpak_rclone.user, pikpak_rclone.password, name=pikpak_rclone.remote)
        else:
            opation_pikpak_go = BasePikpakData(
                mail=pikpak_rclone.user, pd=pikpak_rclone.password, name=pikpak_rclone.remote)
            if opation_pikpak_go.get_vip_day_time_left() <= 0:
                self.opation_pikpak_go = opation_pikpak_go
        if self.opation_pikpak_go:
            return self.opation_pikpak_go
        else:
            return self.pop_not_vip_pikpak()

    def save_pikpak_2(self, pikpak_go: BasePikpakData):
        if self.opation_pikpak_go.mail == pikpak_go.mail:
            logger.info(f"保存pikpak rclone中的账号和现在的账号时同一个这里不做修改")
            return

        data = self.conifg_2_pikpak_rclone[self.opation_index]
        data["pikpak_user"] = pikpak_go.mail
        data["pikpak_password"] = pikpak_go.pd
        logger.debug(self.conifg_2_pikpak_rclone)
        self.save_config()


def radom_password():
    chars = string.ascii_letters+string.digits
    # 得出的结果中字符会有重复的
    return ''.join([random.choice(chars) for i in range(random.randint(8, 11))])


def get_proxy():
    logger.info("获取代理地址中。。。。。")
    ip, proxy_type = pop_prxy_pikpak()
    logger.info(f"获取到的代理:{ip}")
    return ip, proxy_type


def run_all():
    """运行所有的pikpak账号检测
    """
    logger.info("开始执行系统中的会员状态检测")
    alistPikpak: ManagerPikPak = config.alist_enable and ManagerAlistPikpak(
    ) or ManagerRclonePikpak()
    pikpak_go = alistPikpak.pop_not_vip_pikpak()
    while pikpak_go:
        if pikpak_go.try_get_vip():
            vip_day = pikpak_go.get_vip_day_time_left()
            logger.info(f"尝试获取vip成功 当前vip剩余天数{vip_day}")
            pikpak_go = alistPikpak.pop_not_vip_pikpak()
            continue
        HandleSuper(
            get_token=config.get_captcha_callback(),
            get_mailcode=config.get_email_verification_code_callback(),
            email_address=create_one_mail,
            get_password=radom_password,
            get_proxy=get_proxy,
        )
        pikpak: BasePikpakData = BasePikpakData.create()
        time.sleep(60)
        pikpak.reward_vip_upload_file()
        time.sleep(5)
        if pikpak.get_vip_day_time_left() > 0:
            share_id = pikpak_go.start_share_self_files()
            time.sleep(10)
            pikpak.save_share(share_id)
            alistPikpak.save_pikpak_2(pikpak)
            pikpak_go = alistPikpak.pop_not_vip_pikpak()
        # invite_code = pikpak_go.get_self_invite_code()
        # logger.info(f"注册新号填写邀请到:\n{pikpak_go.mail}\n邀请码:\n{invite_code}")
        # pikpak_go_new = crete_invite(invite_code)
        # if not pikpak_go_new:
        #     logger.debug("新建的号有误")
        #     logger.info(f"注册新号失败。。。。。。。。")
        #     break
        # if pikpak_go.get_vip_day_time_left(is_update=True) > 0:
        #     logger.info(f"账号{pikpak_go.mail}现在已经是会员了")
        #     if config.change_model == "all":
        #         # pikpak_go = alistPikpak.pop_not_vip_pikpak()
        #         pass
        #     elif config.change_model == "randam":
        #         pikpak_go = alistPikpak.pop_not_vip_pikpak()
        # if not pikpak_go:
        #     break
        # if pikpak_go_new.get_vip_day_time_left() <= 0:
        #     logger.error(
        #         f"新账号邀请注册有问题 新账号：{pikpak_go_new.mail}的vip都是0天\n填写的邀请信息如下:\ninvite_code:{invite_code}\tmail:{pikpak_go.mail}")
        #     pikpak_go = alistPikpak.pop_not_vip_pikpak()
        #     continue
        # if config.change_model == "none":
        #     continue
        # logger.info(
        #     f"把账号:{pikpak_go.mail},中的所有数据分享到新的账号:{pikpak_go_new.mail} 上")
        # share_id = get_start_share_id(pikpak_go)
        # pikpak_go_new.set_proxy(None)
        # pikpak_go_new.save_share(share_id)
        # alistPikpak.save_pikpak_2(pikpak_go_new)
        # # 新的获取新没有vip的pikpak
        # pikpak_go = alistPikpak.pop_not_vip_pikpak()
    logger.info("Over")


def 所有的没有vip的PikPak():
    logger.info("开始获取本地所有不是会员的配置")
    base_pikpak: ManagerPikPak = config.alist_enable and ManagerAlistPikpak(
    ) or ManagerRclonePikpak()
    return base_pikpak.get_all_not_vip()


def 注册新号激活(pikpak: PikPak = None):
    return crete_invite(pikpak.get_self_invite_code())


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


if __name__ == "__main__":
    set_def_callback()
    # if config.telegram_api and len(config.telegram_api) > 1:
    #     telegram.Telegram()
    run_all()
    # alistPikpak = AlistPikpak()
    # pikpak_go = alistPikpak.pop_not_vip_pikpak()
    # invite_code = pikpak_go.get_self_invite_code()
    # pikpak_go_new = crete_invite(invite_code)
    # get_start_share_id("mwrtye3718@tenvil.com","098poi")
    # https://mypikpak.com/s/VNzDxRlK3CYk0Z6HfkzTEw1uo1
    # pikpak = crete_invite(78269860)
    # print(pikpak.mail)

    # rclone_conifgs = get_save_json_config()
    # print(rclone_conifgs)
    # index = 1
    # rclone = rclone_conifgs[index]
    # data = rclone_conifgs[index]
    # data["pikpak_user"] = data["pikpak_user"]+"0909090"
    # # rclone.update(data)
    # print(rclone_conifgs)
    # copye_list_2_rclone_config()

    # logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # logger.addHandler(handler)
    # email = "bpzaof1188@nuclene.com"
    # password = "098poi"
    # pikpak_ = PikPak(email, password)
    # from proxy_ip import pingPikpak
    # # pingPikpak("43.134.68.153:3128 http", [])
    # # pikpak_.set_proxy("43.134.68.153:3128")
    # run_new_test(pikpak_)
    # https://mypikpak.com/s/VO0UAyoBjunwgtyhTtnMWl5Lo1
