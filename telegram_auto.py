# telebot
import re
import time
from telebot import TeleBot
from telebot.types import Message
from config.config import telegram_api, set_log, set_captcha_callback
from main import main


class TelegramBot(object):
    bot = None
    opation_id = None
    token_callback = None
    token = None
    runing = False

    def _start_message(self, message: Message):
        # self.bot.reply_to(message, "你好！如果需要验证了我会这里发送消息到你的TG")
        if self.runing:
            self.bot.send_message(
                self.opation_id, "你好！服务正在运行中。。。。。请等待结束在启动")
            return
        self.opation_id = message.chat.id
        self.bot.send_message(
            self.opation_id, "你好！现在服务器开启了自动注册模式稍后会发送验证消息到你的tg请获取到token后回复验证消息")
        self.runing = True
        try:
            main()
        except Exception as e:
            self.send_print_to_tg(e)
        self.runing = False
        # self.send_get_token("www.google.com")

    def send_print_to_tg(self, message_text):
        """发送消息到TG

        Args:
            message_text (_type_): _description_
        """
        self.bot.send_message(
            self.opation_id,
            message_text
        )

    def send_get_token(self, url: str):
        """发送验证url消息到TG TG需要回复才继续运行

        Args:
            url (str): 需要验证的url

        Returns:
            _type_: _description_
        """
        self.token = None
        self.bot.send_message(
            self.opation_id,
            "请获取一下url的验证 并回复token到下一条消息"
        )
        __token_message = self.bot.send_message(
            self.opation_id,
            url
        )
        self.bot.register_for_reply(
            __token_message, self.__reply_token)
        while not self.token:
            time.sleep(0.1)
        self.bot.clear_reply_handlers(__token_message)
        return self.token

    def __reply_token(self, message: Message):
        captcha_token = message.text
        captcha_token = self.__find_str_token(captcha_token)
        self.token = captcha_token

    def __init__(self) -> None:
        set_log(self.send_print_to_tg)
        set_captcha_callback(self.send_get_token)
        self.bot = TeleBot(telegram_api, num_threads=5)
        self.bot.register_message_handler(
            self._start_message, commands=['start'])
        self.bot.infinity_polling()

    def __find_str_token(self, strs: str = ""):
        str_start = "captcha_token="
        str_end = "&expires_in"
        if str_start in strs:
            strs = strs[
                strs.find(str_start)+len(str_start):
            ]
        if str_end in strs:
            strs = strs[0:strs.find(str_end)]
        return strs


if __name__ == "__main__":
    tg = TelegramBot()
    # str___ = "xlaccsdk01://xunlei.com/callback?state=dharbor&state=undefined&captcha_token=ck0.metBhXNbM5Rxfbx6aOMweTUXbVmc3YioMrhkR8gy7gGliqN-8KhWNWn95N6KNAhBkuThEZt_eJcEEgK8wC0klfT2TwyTCCYGGTQUsD_G5eoOoevuuBt6J-jXCL7P_284UKdyTOUSrEEOaiyC0f-5CbgudPBietbj2aKlTu_G_sUQo-pzeIRJw9mj-pgU9NpCfh82acUA7rkacTr3EYYZOjEINB7MiMYxGx2Rn1EKPBeHEKURQSI5UdMUk7rGGSm0xC_m7Yb1UV25kzagH1JaK6l2RnYUZZpwkNC1Xsc4xVHug5oeIZwoMiMdC_YgLPAojIC4yXKZ3F2a8uFKxxsO21BDdUGIDctBipNeK4pJMOAfSGv9dK1cBNWbEUPXNS2yRamiWU-8fv5xTlP99G-vLSjThRykWsY7-82c_pZk0lnnwh3ynVOYtULtaVhKRLsVN3oeTFZWzJcvsa1E43yXGIA8yVH6Ep_ugOrbDzAz0kMkB4E2RZvcy-OmFrjrbLG27T1ul9yToI7sEmyz0ErqEQ&expires_in=600"
    # find_str_token(str___)
    # print()
    # while not tg.opation_id:
    #     time.sleep(0.2)
    # time.sleep(5)
    # tg.send_print_to_tg("eieieieieii")
    # time.sleep(2)
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # token = tg.send_get_token(temp_url)
    # print(token)
