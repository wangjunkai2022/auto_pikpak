import logging
import time
from pikpak.chrome_pikpak import ChromePikpak, Handle

logger = logging.getLogger("PikPakSuper")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class HandleSuper(Handle):
    def __def_email_address(self) -> str:
        """
        默认获取一个邮箱的回调
        """
        mail_input = input(f"请输入邮箱\n")
        return mail_input

    def __def_password(self) -> str:
        pd_input = input(f"请输入密码\n")
        return pd_input

    def __def_proxy(self) -> str:
        proxy_input = input(f"请输入代理地址\n")
        return proxy_input

    __get_email_address_callback = None
    __get_password_callback = None
    __get_proxy_callback = None

    def __init__(self, get_token=None, get_mailcode=None, email_address=None, get_password=None, get_proxy=None) -> None:
        super().__init__(get_token, get_mailcode)
        self.__get_email_address_callback = email_address or self.__def_email_address
        self.__get_password_callback = get_password or self.__def_password
        self.__get_proxy_callback = get_proxy or self.__def_proxy

    def run_get_mail_address(self) -> str:
        return self.__get_email_address_callback()

    def run_get_password(self) -> str:
        return self.__get_password_callback()

    def run_get_proxy(self) -> str:
        return self.__get_proxy_callback()


class PikPakSuper(ChromePikpak):

    @staticmethod
    def create(handler: HandleSuper = HandleSuper()):
        mail = handler.run_get_mail_address()
        pd = handler.run_get_password()
        proxy = handler.run_get_proxy()
        _pikpak = PikPakSuper(mail, pd)
        _pikpak.setHandler(handler)
        _pikpak.set_proxy(*proxy)
        logger.info(f"开始注册\n账号:{mail}\n密码:{pd}")
        _pikpak.register()
        _pikpak.run_test()
        return _pikpak

    def run_test(self):
        """
        随机运行 模拟人为操作
        """
        self.login()
        self.me()
        self.configs()
        self.lbsInfo()
        self.user_settings_bookmark()
        self.about()
        self.inviteCode()
        self.vip_checkInvite()
        self.vip_info()
        self.vip_inviteList()
        self.upgradeToPro()
        self.inviteInfo()
        self.task_free_vip()
        self.task_reference_resource()
        self.check_task_status()
        self.invite()

    # 快捷操作

    def get_vip_day_time_left(self) -> int:
        """
        获取当前pikpak账号的剩余vip天数
        """
        self.login()
        vip_data = self.vip_info()
        def_day_num = -9999
        try:
            def_day_num = vip_data.get('data').get("vipItem")[
                0].get("surplus_day", def_day_num)
        except Exception as e:
            logger.debug(f"获取vip剩余天数错误{e}")
            # def_day_num = -9999
        return def_day_num
    # 获取自己的邀请码

    def try_get_vip(self):
        """
        尝试获取vip
        """
        self.login()
        vip_day = self.get_vip_day_time_left()
        if vip_day > 0:
            logger.debug('当前vip没过期 这里不获取vip')
            return True
        self.verifyRecaptchaToken()
        self.reward_vip_upload_file()
        time.sleep(5)
        if self.try_get_vip():
            return True
        self.reward_vip_install_web_pikpak_extension()
        time.sleep(5)
        if self.try_get_vip():
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
            if file.get("name") == 'My Pack' or file.get("name") == 'Pack From Shared':
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
        json_data = self.file_batch_share(fils_id, expiration_days=7)
        logger.debug(json_data)
        return json_data

    def save_share(self, shareid: str) -> None:
        """
        保存人家的分享到自己的账号
        """
        self.login()
        self.save_share_2_self(shareid)


if __name__ == "__main__":
    # email = "covaxe9867@biowey.com"
    # password = "2dewmJR1"
    # # email = 'sotag69939@alientex.com'
    # # password = '12poi900'
    # pikpak_ = PikPakSuper(email, password)
    # pikpak_.start_share_self_files()
    PikPakSuper.create()
