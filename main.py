import asyncio

from pikpak import PikPak
from chmod import open_url2token
from ips import thread_get_all_ip
from mail import create_one_mail, get_new_mail_code
import config

import threading

invites = config.invites


def runInvite(invite, ips):
    pik_go = None
    try:
        _mail = create_one_mail()
        pik_go = PikPak(_mail, "098poi",
                        captcha_token_callback=open_url2token,
                        main_callback=get_new_mail_code,
                        invite=str(invite)
                        )
        pik_go.set_proxy(*ips.pop(0))
        pik_go.run_req_2invite()
        if pik_go.isInvise:
            return
        else:
            print(f"{invite} 注册失败！重新注册")
            runInvite(invite, ips)
    except Exception as e:
        print(f"{invite} 注册失败！ Error{e}")
        if pik_go.inviseError:
            print(f"开始重新注册")
            runInvite(invite, ips)


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # get_future = asyncio.ensure_future(get_pikpak_proyxs())  # 相当于开启一个future
    # loop.run_until_complete(get_future)  # 事件循环
    # ips = get_future.result()
    ips = thread_get_all_ip()
    # mail = create_one_mail()
    # mail = "uppuki8692@maxric.com"
    # pd = "098poi"
    # invite_index = 0
    # invite = invites[invite_index].get("invite_number")
    ths = []
    for invite in invites:
        th = threading.Thread(target=runInvite, args=(invite.get("invite_number"), ips))
        th.start()
        ths.append(th)

    for th in ths:
        th.join()
    # for ip in ips:
    #     try:
    #         print(f"main:{mail} \nip:{ip} \ninvite:{invite}")
    #         # proxy = ip.split(" ")
    #         pik_go.set_proxy(*ip)
    #         if pik_go.isReqMail:
    #             pik_go.run_login_2invite()
    #         else:
    #             pik_go.run_req_2invite()
    #         if pik_go.isInvise:
    #             print(f"成功注册{mail} 并填写了{invite}这个邀请码")
    #             invite_index += 1
    #             if invite_index < len(invites):
    #                 mail = create_one_mail()
    #                 invite = invites[invite_index].get("invite_number")
    #                 pik_go = PikPak(mail, pd, captcha_token_callback=open_url2token, main_callback=get_new_mail_code,
    #                                 invite=str(invite))
    #             else:
    #                 break
    #         elif pik_go.inviseError:
    #             print(f'邀请注册失败{pik_go.inviseError}')
    #             if invite_index < len(invites):
    #                 mail = create_one_mail()
    #                 invite = invites[invite_index].get("invite_number")
    #                 pik_go = PikPak(mail, pd, captcha_token_callback=open_url2token, main_callback=get_new_mail_code,
    #                                 invite=str(invite))
    #             else:
    #                 break
    #     except BaseException as e:
    #         print(e)
