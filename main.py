import asyncio

from pikpak import PikPak
from chmod import open_url2token
from ips import get_pikpak_proyxs

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    get_future = asyncio.ensure_future(get_pikpak_proyxs())  # 相当于开启一个future
    loop.run_until_complete(get_future)  # 事件循环
    ips = get_future.result()
    mail = "wipit83288@darkse.com"
    pd = "098poi"
    invite = 92196679
    for ip in ips:
        try:
            proxy = ip.split(" ")[0]
            pik_go = PikPak(mail, pd, captcha_token_callback=open_url2token, proxy=proxy, invite=str(92196679),
                            run=True)
            print(f"成功注册{mail} 并填写了{invite}这个邀请码")
            break
        except BaseException as e:
            print(e)
