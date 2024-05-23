# telebot
import re
import time
from telebot import TeleBot
from telebot.types import Message
from config import telegram_api
from main import main


class TelegramBot(object):
    # bot = TeleBot(telegram_api, num_threads=5)
    # def __init__(self)

    # @bot.message_handler(commands=['start'])
    # def send_welcome(self, message):
    #     self.bot.reply_to(message, "现在我们开始 当需要验证时会发送消息到你的TG")

    # bot.infinity_polling()
    bot = None

    opation_id = None

    token_callback = None

    token = None

    def _start_message(self, message: Message):
        # self.bot.reply_to(message, "你好！如果需要验证了我会这里发送消息到你的TG")
        self.opation_id = message.chat.id
        self.bot.send_message(
            self.opation_id, "你好！现在服务器开启了自动注册模式稍后会发送验证消息到你的tg请获取到token后回复验证消息")
        main(self.send_get_token)
        # self.send_get_token("www.google.com")

    def send_print_to_tg(self, message_text):
        self.bot.send_message(
            self.opation_id,
            message_text
        )

    def send_get_token(self, url: str):
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
        captured_url = message.text
        str_start = "captcha_token="
        str_end = "&expires_in"
        search = re.search(f"{str_start}.*{str_end}", captured_url)
        if search:
            captcha_token = search.group()[len(str_start):-len(str_end)]
        else:
            captcha_token = captured_url
        self.token = captcha_token

    def __init__(self) -> None:
        self.bot = TeleBot(telegram_api, num_threads=5)
        self.bot.register_message_handler(
            self._start_message, commands=['start'])
        self.bot.infinity_polling()


if __name__ == "__main__":
    tg = TelegramBot()
    # print()
    # while not tg.opation_id:
    #     time.sleep(0.2)
    # time.sleep(5)
    # tg.send_print_to_tg("eieieieieii")
    # time.sleep(2)
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIUwwAS8emJf07i6IzskAZS5t1PVY4aenJNHuNWJta1Xk8Lum03XvyU6t1yolwXbfpHFtDqs1R3WJj0m6gwEaLuDzXbn2wh90nh0eOG6aZgD6HOcW5j1LrNhu-lT2zpS_ngL2ywOujjqZRrpfZjjDIh2HCNaYnJnDvsIYDLiBDE1-lg9PtauuDMpuN78O2e402Ar7CMHB8JKrAWxZ4X4xQBErkrT9b-2UH4d3gLdvjYSi2F2VZbe3UQlBq_KAmU_8zJrFUqiazvOi3m1QzIa2vjfQOfyC9OQlMpQ8rb56sLOPR8K4RE7TTO-uQyvcagViw82kkUJunyCtcIlJlLXny_jNeh9RuHOlx5MtegFwd-j1JVVHiKMvUkXjBxJv-rWHYGCYMxJUp4UOJjUjDLXQYgF&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.GNUSo4m17OpSstL-qSAzyBUQyjUV2P0p5bEYgZzV-hljkShTX_6gRg2hcxJPMliURNP7BY0kAg2pwJO3sCvFnvmjh3cWDIA-1VO0sf9kJIWMdlxDACQF1BCd60Eouu78b8-kzWbzzEKX9P677Uh47e9tIuJ--9u0i1GPcqTtMUbv6YhNMA7uBJ9o1dSH9wGkGUR96TmtKgHRWBqot_iKDgm9RK1vx-SCuH0ok1amd2rwqMLJL9JKdfIWEYBEDHAXiLJWQWBuLbnoUGDfeffAkU45tD8Z5OdSzITlW93SjfD0YEvi45kCPXu_YfwAMEHwKvn7ayzeydXWPWijTA1ORVDL0W5hWAnoyO9xsBfT94yp_Kw_w1kv9vTw5PaZUmLRioP6Y6VD0N-haNqdgvOh2mZ2VDLYt1z1HotAO05neMtWNthDR-QQS9FLwKASWib6SIUNBx3MGcEz0qQV9YRol9Y3MTugAe80YkT4EjLM39M&credittype=1&device_id=b7742fb931374efe85756ee936da40e5&deviceid=b7742fb931374efe85756ee936da40e5&event=xbase-auth-verification&hl=zh-TW&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxunlei.com%2Fcallback%3Fstate%3Ddharbor&traceid="  # 请替换为实际的网页地址
    # token = tg.send_get_token(temp_url)
    # print(token)
