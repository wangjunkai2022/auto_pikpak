import logging
import random
import time
import traceback
from types import FunctionType, MethodType
import requests
from pikpak.android_pikpak import AndroidPikPak
from pikpak.chrome_pikpak import ChromePikpak, Handle

logger = logging.getLogger("PikPakSuper")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class HandleSuper(Handle):
    def def_email_address(self) -> str:
        """
        默认获取一个邮箱的回调
        """
        mail_input = input(f"请输入邮箱\n")
        return mail_input

    def def_password(self) -> str:
        pd_input = input(f"请输入密码\n")
        return pd_input

    get_email_address_callback = None
    get_password_callback = None

    def __init__(
        self,
        get_token=None,
        get_mailcode=None,
        email_address=None,
        get_password=None,
        get_proxy=None,
    ) -> None:
        super().__init__(get_token, get_mailcode, get_proxy)
        self.get_email_address_callback = email_address
        self.get_password_callback = get_password

    def run_get_mail_address(self) -> str:
        type__ = type(self.get_email_address_callback)
        logger.debug(type__)
        if self.get_email_address_callback and (isinstance(self.get_email_address_callback, FunctionType) or isinstance(self.get_email_address_callback, MethodType)):
            return self.get_email_address_callback()
        else:
            return self.def_email_address()

    def run_get_password(self) -> str:
        if self.get_password_callback and (isinstance(self.get_password_callback, FunctionType) or isinstance(self.get_password_callback, MethodType)):
            return self.get_password_callback()
        else:
            return self.def_password()


class PikPakSuper(AndroidPikPak):
    @staticmethod
    def create(handler: HandleSuper = HandleSuper()):
        # tmp = handler.run_get_mail_address()
        # tmp = handler.run_get_maincode(tmp)
        # tmp = handler.run_get_password()
        # tmp = handler.run_get_token("https://google.com")
        # # tmp = handler.run_get_proxy()
        # return None

        mail = handler.run_get_mail_address()
        proxy = handler.run_get_proxy()
        pd = handler.run_get_password()
        _pikpak = PikPakSuper(mail, pd)
        _pikpak.setHandler(handler)
        _pikpak.set_proxy(*proxy)
        logger.info(f"开始注册\n账户:{mail}\n密码:{pd}")
        while True:
            try:
                _pikpak.register()
                break
            except requests.exceptions.ProxyError:
                logger.info("代理异常 重新获取一个代理")
                proxy = handler.run_get_proxy()
                _pikpak.set_proxy(*proxy)
            except Exception as e:
                if str(e).startswith("网络连接错误"):
                    proxy = handler.run_get_proxy()
                    _pikpak.set_proxy(*proxy)
                    _pikpak.save_self()
                    continue
                logger.error(str(e))

        # _pikpak.run_test()
        return _pikpak

    def run_test(self):
        """
        随机运行 模拟人为操作
        """
        self.login()
        self.me()

        callbacks = [
            self.me,
            self.configs,
            self.lbsInfo,
            self.user_settings_bookmark,
            self.invite,
            self.vip_info,
            self.about,
            self.inviteCode,
            self.vip_checkInvite,
            self.test_config_v1_drive,
            self.vip_inviteList,
            self.upgradeToPro,
            self.inviteInfo,
            self.task_free_vip,
            self.task_reference_resource,
            self.check_task_status,
            self.invite,

            self.me,
            self.configs,
            self.lbsInfo,
            self.user_settings_bookmark,
            self.invite,
            self.vip_info,
            self.about,
            self.inviteCode,
            self.vip_checkInvite,
            self.test_config_v1_drive,
            self.vip_inviteList,
            self.upgradeToPro,
            self.inviteInfo,
            self.task_free_vip,
            self.task_reference_resource,
            self.check_task_status,
            self.invite,
        ]
        random.shuffle(callbacks)
        for callback in callbacks:
            callback()

        
        logger.debug(f"文件操作模拟")
        try:
            file_list = self.file_list(parent_id="*")
            logger.debug(f"文件列表:{file_list}")
            events = self.events(size=50)
            logger.debug(f"最近添加文件:{events}")
            file_id = events.get("events")[0].get("file_id")
            down_url = self.get_download_url(file_id)
            logger.debug(f"down_url:{down_url}")
        except Exception as e:
            logger.error(f"文件模拟错误 error:{e}")
            trace = traceback.print_exc()
            logger.error(f"trace:{trace}")

        self.random_download_magnet()

        logger.debug(f"文件操作模拟完毕")
        
    # 快捷操作
    def random_download_magnet(self):
        events = self.events()
        if len(events.get("events")) == 1 and events.get("events")[0].get("type") == 'TYPE_RESTORE' and events.get("events")[0].get("type_name") == 'Add' and "PikPak" in events.get("events")[0].get("file_name"):
            from torrent import random_one_magnet
            magnet = random_one_magnet()
            logger.info(f"开始下载一个种子:\n{magnet}")
            download = self.offline_download(magnet)
            logger.debug(download)
        else:
            logger.debug(f"已经下载过一次种子文件了")

    def get_vip_day_time_left(self) -> int:
        """
        获取当前pikpak账户的剩余vip天数
        """
        
        def_day_num = -9999
        try:
            self.login()
            vip_data = self.vip_info()
            def_day_num = (
                vip_data.get("data").get("vipItem")[-1].get("surplus_day", def_day_num)
            )
        except Exception as e:
            logger.debug(f"获取vip剩余天数错误{e}")
        return def_day_num

    # 获取自己的邀请码

    def try_get_vip(self):
        """
        尝试获取vip
        """
        return False
        self.login()
        vip_day = self.get_vip_day_time_left()
        if vip_day > 0:
            logger.debug("当前vip没过期 这里不获取vip")
            return True
        self.verifyRecaptchaToken()
        try:
            self.reward_vip_upload_file()
        except Exception as e:
            logger.error(str(e))
        time.sleep(5)
        vip_day = self.get_vip_day_time_left()
        if vip_day > 0:
            logger.debug("当前是vip了")
            return True
        self.reward_vip_install_web_pikpak_extension()
        time.sleep(5)
        vip_day = self.get_vip_day_time_left()
        if vip_day > 0:
            logger.debug("当前是vip了")
            return True
        return False

    def get_self_invite_code(self) -> str:
        """
        获取自己的邀请码
        """
        self.login()
        invite_data = self.inviteCode()
        return str(invite_data.get("code"))

    def start_share_self_files(self) -> str:
        """
        分享自己的文件
        """
        self.login()
        for count in range(3):
            try:
                json_data = self.path_to_id("Pack From Shared")
                if len(json_data) == 1:
                    id_Pack_From_Shared = json_data[-1].get("id")
                    # 获取Pack From Shared文件夹下的所有文件夹
                    json_data = self.file_list(parent_id=id_Pack_From_Shared)
                    if len(json_data.get("files")) <= 0:
                        id_Pack_From_Shared = None
                else:
                    id_Pack_From_Shared = None
                # 获取Pack From Shared文件夹下的所有文件夹

                json_data = self.file_list(parent_id=id_Pack_From_Shared)
                # 需要分享的文件夹id
                fils_id = []
                for file in json_data.get("files"):
                    if (
                        file.get("name") == "My Pack"
                        or file.get("name") == "Pack From Shared"
                    ):
                        pass
                    else:
                        fils_id.append(file.get("id"))
                # for file in invite.get("share", []):
                #     get_future = asyncio.ensure_future(pikpak_api.path_to_id(file))
                #     main_loop.run_until_complete(get_future)
                #     result = get_future.result()
                #     fils_id.append(result[-1].get("id"))
                if len(fils_id) < 1:
                    raise Exception("没有分享文件")
                json_data = self.file_batch_share(fils_id)
                logger.debug(json_data)
                return json_data
            except Exception as e:
                logger.error(f"分享时报错了\nerror:{e}\n{count}/3")
                time.sleep(30)
                self.login_out()
                time.sleep(10)
                self.login()

        raise Exception("分享失败")

    def save_share(self, shareid: str) -> None:
        """
        保存人家的分享到自己的账户
        """
        self.login()
        return self.save_share_2_self(shareid)


if __name__ == "__main__":
    email = "alsljs4853@maxric.com"
    password = "ezZd73li8"
    pikpak_ = PikPakSuper(
        email,
        password,
    )
    pikpak_.login()
    pikpak_.vip_info()
    pikpak_.set_activation_code("39576161")
    # PikPakSuper.create()
