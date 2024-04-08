import asyncio

from pikpak import PikPak
from chmod import open_url2token
from ips import get_pikpak_proyxs
from mail import create_one_mail, get_new_mail_code
import config

invites = config.invites

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    get_future = asyncio.ensure_future(get_pikpak_proyxs())  # 相当于开启一个future
    loop.run_until_complete(get_future)  # 事件循环
    ips = get_future.result()
    mail = create_one_mail()
    # mail = "uppuki8692@maxric.com"
    pd = "098poi"
    invite_index = 0
    invite = invites[invite_index].get("invite")
    pik_go = PikPak(mail, pd, captcha_token_callback=open_url2token, main_callback=get_new_mail_code,
                    invite=str(invite))
    for ip in ips:
        try:
            print(f"main:{mail} \nip:{ip} \ninvite:{invite}")
            proxy = ip.split(" ")[0]
            pik_go.set_proxy(proxy)
            if pik_go.isReqMail:
                pik_go.run_login_2invite()
            else:
                pik_go.run_req_2invite()
            if pik_go.isInvise:
                print(f"成功注册{mail} 并填写了{invite}这个邀请码")
                invite_index += 1
                if invite_index < len(invites):
                    mail = create_one_mail()
                    invite = invites[invite_index].get("invite")
                    pik_go = PikPak(mail, pd, captcha_token_callback=open_url2token, main_callback=get_new_mail_code,
                                    invite=str(invite))
                else:
                    break
        except BaseException as e:
            print(e)
