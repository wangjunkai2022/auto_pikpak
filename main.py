from pikpak import PikPak
from chmod import open_url2token
from ips import thread_get_all_ip
from mail import create_one_mail, get_new_mail_code
import config

import threading

invites = config.invites


def runInvite(invite, ips):
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
        # if not pik_go.inviseError:
        print(f"开始重新注册")
        runInvite(invite, ips)


if __name__ == "__main__":
    ips = thread_get_all_ip()
    ths = []
    for invite in invites:
        th = threading.Thread(target=runInvite, args=(invite.get("invite_number"), ips))
        th.start()
        ths.append(th)

    for th in ths:
        th.join()
