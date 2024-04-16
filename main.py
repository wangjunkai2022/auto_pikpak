from pikpak import PikPak
from chmod import open_url2token
from ips import thread_get_all_ip
from mail import create_one_mail, get_new_mail_code
import config
import asyncio
from pikpakapi import PikPakApi, PikpakException
import threading

invites = config.pikpak_user

def_dp = "098poi"


def start_share(invite):
    pikpak_api = PikPakApi(invite.get("mail"), def_dp)
    # 创建一个事件循环thread_loop
    main_loop = asyncio.get_event_loop()
    get_future = asyncio.ensure_future(pikpak_api.login())
    main_loop.run_until_complete(get_future)
    fils_id = []
    for file in invite.get("share", []):
        get_future = asyncio.ensure_future(pikpak_api.path_to_id(file))
        main_loop.run_until_complete(get_future)
        result = get_future.result()
        fils_id.append(result[-1].get("id"))
    get_future = asyncio.ensure_future(pikpak_api.file_batch_share(fils_id, expiration_days=7))
    main_loop.run_until_complete(get_future)
    result = get_future.result()
    print(result)
    return result.get("share_url")


def saveUrlToPikpak(mail, url):
    pikpak_api = PikPakApi(mail, def_dp)
    main_loop = asyncio.get_event_loop()
    get_future = asyncio.ensure_future(pikpak_api.login())
    main_loop.run_until_complete(get_future)

    get_future = asyncio.ensure_future(pikpak_api.offline_download(url))
    main_loop.run_until_complete(get_future)
    result = get_future.result()
    print(result)


def runInvite(invite, ips):
    try:
        _mail = create_one_mail()
        pik_go = PikPak(_mail, def_dp,
                        captcha_token_callback=open_url2token,
                        main_callback=get_new_mail_code,
                        invite=str(invite.get("invite_number"))
                        )
        ip, proxy_type = ips.pop(0)
        pik_go.set_proxy(ip, proxy_type)
        pik_go.run_req_2invite()
        if pik_go.isInvise:
            print(f"{invite} 邀请注册成功")
            url = start_share(invite)
            saveUrlToPikpak(_mail, url)
            input_str = f"_mail:{_mail}\n"
            temp_file = "pikpak_user.txt"
            with open(temp_file, 'a') as f:  # 设置文件对象
                f.write(input_str)  # 将字符串写入文件中
            return
        else:
            print(f"{invite} 注册失败！重新注册")
            runInvite(invite, ips)
    except Exception as e:
        print(f"{invite} 注册失败！ Error{e}")
        if "empty list" in e.__str__():
            return
        # if not pik_go.inviseError:
        print(f"开始重新注册")
        runInvite(invite, ips)


if __name__ == "__main__":
    # ips = thread_get_all_ip()
    for invite in invites:
        # runInvite(invite, ips)
        start_share(invite)
    # ths = []
    # for invite in invites:
    #     th = threading.Thread(target=runInvite, args=(invite.get("invite_number"), ips))
    #     th.start()
    #     ths.append(th)
    # 
    # for th in ths:
    #     th.join()
