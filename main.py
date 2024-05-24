import json
from pikpak import PikPak, crete_invite
from chmod import open_url2token
import config
import asyncio
from PikPakAPI.pikpakapi import PikPakApi, PikpakException
import alist
from mail import get_new_mail_code


def get_start_share_id(mail, password):
    pikpak_api = PikPakApi(mail, password)
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
    print(result)
    return result.get("share_id", None)


class AlistPikpak:
    pikpak_user_list = None
    alist_go = None
    opation_pikpak_go: PikPak = None

    def __init__(self):
        self.alist_go = alist.Alist()
        self.alist_go.saveToNowConif()
        self.pikpak_user_list = self.alist_go.get_all_pikpak_storage()

    # 直接pop一个Alsit中的一个Vip的剩余天数小于0的pikpak登陆
    def pop_not_vip_pikpak(self) -> PikPak:
        if len(self.pikpak_user_list) <= 0:
            return None
        if self.pop_pikpak().get_vip_day_time_left() < 0:
            return self.opation_pikpak_go
        else:
            return self.pop_not_vip_pikpak()

    # 直接pop一个Alsit中的一个pikpak登陆
    def pop_pikpak(self) -> PikPak:
        pikpak_data = self.pikpak_user_list.pop(0)
        self.opation_pikpak_go = PikPak(
            mail=pikpak_data.get("username"),
            pd=pikpak_data.get("password"),
            run=False)
        return self.opation_pikpak_go

    def change_self_pikpak_2_alist(self, pikpak_go: PikPak):
        storage_list = self.alist_go.get_storage_list()
        for data in storage_list.get("content"):
            addition = json.loads(data.get("addition"))
            if addition.get("username") == self.opation_pikpak_go.mail:
                addition["username"] = pikpak_go.mail
                addition["password"] = pikpak_go.pd
                data["addition"] = json.dumps(addition)
                print(data)
                self.alist_go.update_storage(data)
            print(addition)


def main():
    log = config.get_log()
    log("开始执行Alist中的存储检测")
    alistPikpak = AlistPikpak()
    pikpak_go = alistPikpak.pop_not_vip_pikpak()
    while pikpak_go:
        invite_code = pikpak_go.get_self_invite_code()
        log(f"注册新号填写邀请到:\n{pikpak_go.mail}\n邀请码:\n{invite_code}")
        pikpak_go_new = crete_invite(invite_code)
        if not pikpak_go_new:
            print("新建的号有误")
            log(f"注册新号失败。。。。。。。。")
            break
        if pikpak_go.get_vip_day_time_left() > 0:
            log(f"账号{pikpak_go.mail}现在已经是会员了")
            pikpak_go = alistPikpak.pop_not_vip_pikpak()
        if not pikpak_go:
            break
        if pikpak_go_new.get_vip_day_time_left() <= 0:
            continue
        log(f"把账号:{pikpak_go.mail},中的所有数据分享到新的账号:{pikpak_go_new.mail} 上")
        share_id = get_start_share_id(
            pikpak_go.mail, pikpak_go.pd
        )
        pikpak_go_new.set_proxy(None)
        pikpak_go_new.save_share(share_id)
        alistPikpak.change_self_pikpak_2_alist(pikpak_go_new)
        # 新的获取新没有vip的pikpak
        pikpak_go = alistPikpak.pop_not_vip_pikpak()
    log("Over")


if __name__ == "__main__":
    config.set_captcha_callback(open_url2token)
    config.set_email_verification_code_callback(get_new_mail_code)
    main()
    # alistPikpak = AlistPikpak()
    # pikpak_go = alistPikpak.pop_not_vip_pikpak()
    # invite_code = pikpak_go.get_self_invite_code()
    # pikpak_go_new = crete_invite(invite_code)
