# telebot
# from enum import StrEnum
from enum import Enum
import pickle
import logging
import re
import time
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config.config import telegram_api, set_log, set_captcha_callback
from main import BasePikpakData, ManagerRclonePikpak, run_all, 注册新号激活, 所有的没有vip的PikPak

loging_names = [
    "main", "alist", "mail", "captch_chomd", "pikpak", "Rclone", "telegram",
]

logger = logging.getLogger("telegram")


class OpationEnum(Enum):
    挂载Rclone = "选择需要挂载的Rclone远程",
    激活PikPak = "选择需要注册激活的PikPak",


class TelegramBot(object):
    bot = None
    opation_id = None
    token_callback = None
    token = None
    runing = False
    __reply_message = None

    temp_pikpaks = []

    def _start_message(self, message: Message):
        if not self.opation_id:
            self.opation_id = message.chat.id
        # self.bot.reply_to(message, "你好！如果需要验证了我会这里发送消息到你的TG")
        markup = ReplyKeyboardMarkup()
        markup.add(KeyboardButton("/扫描所有"))
        markup.add(KeyboardButton("/交互模式"))
        markup.add(KeyboardButton("/挂载Rclone"))

        self.bot.send_message(chat_id=message.chat.id,
                              text="选择运行方式:", reply_markup=markup)

    def send_print_to_tg(self, message_text):
        """发送消息到TG

        Args:
            message_text (_type_): _description_
        """
        self.bot.send_message(self.opation_id,
                              message_text, disable_notification=True)

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
            "请获取一下url的验证 并回复token到下一条消息", disable_notification=True
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

    def _全部扫描模式(self, message: Message):
        if self.runing:
            self.bot.send_message(
                self.opation_id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.opation_id = message.chat.id
        self.bot.send_message(
            self.opation_id, "你好！现在服务器开启了自动注册模式稍后会发送验证消息到你的tg请获取到token后回复验证消息", disable_notification=True)
        self.runing = True
        try:
            run_all()
        except Exception as e:
            self.send_print_to_tg(e)
        self.runing = False
    mount_rclone = []

    def _挂载Rclone(self, message: Message):
        self.opation_id = message.chat.id
        self.rclone_manager = ManagerRclonePikpak()
        index = 0
        markup = InlineKeyboardMarkup(row_width=2)
        for rclone_conifg in self.rclone_manager.json_config:
            btn = InlineKeyboardButton(
                rclone_conifg.remote, callback_data=str(index),)
            markup.add(btn)
            index += 1
        self.__reply_message = self.bot.send_message(message.chat.id, OpationEnum.挂载Rclone.value,
                                                     reply_markup=markup)

    def _交互模式(self, message: Message):
        self.opation_id = message.chat.id
        # markup = InlineKeyboardMarkup(row_width=2)
        # markup.add(InlineKeyboardButton("test", callback_data='pikpak',))
        # if self.__reply_message:
        #     self.bot.send_message(
        #         message.chat.id, "交互模式上一个还没处理完 请等待完成", disable_notification=True)
        #     return
        self.temp_pikpaks = 所有的没有vip的PikPak()
        markup = InlineKeyboardMarkup(row_width=2)
        index = 0
        for pikpak in self.temp_pikpaks:
            btn = InlineKeyboardButton(
                pikpak.name, callback_data=str(index),)
            markup.add(btn)
            index += 1
        self.__reply_message = self.bot.send_message(message.chat.id, OpationEnum.激活PikPak.value,
                                                     reply_markup=markup)

    def __call_back(self, call: CallbackQuery):
        if call.data:
            index = int(call.data)
            if call.message.text == OpationEnum.激活PikPak.value[0]:
                pikpak = self.temp_pikpaks[index]
                self.bot.send_message(call.message.chat.id,
                                      f"正在注册新号中 请等待 邀请的号是{pikpak.mail}")
                new_pikpak = 注册新号激活(pikpak)
                self.bot.send_message(call.message.chat.id,
                                      f"注册新号成功\n{new_pikpak.mail}")
                self.__reply_message = None
                self.temp_pikpaks = []
            elif call.message.text == OpationEnum.挂载Rclone.value:
                pikpak = self.rclone_manager.conifg_2_pikpak_rclone(
                    self.rclone_manager.json_config[index])
                pikpak.run_mount()

    def __reply_button(self, call: CallbackQuery):
        # self.bot.send_message(call.message.chat.id, f"注册新号成功\n{call.data}")
        # if message.date and isinstance(message.date, BasePikpakData):
        #     new_pikpak = 注册新号激活(message.date)
        #     self.bot.send_message(f"注册新号成功\n{new_pikpak.mail}")
        # self.bot.clear_reply_handlers(self.__reply_message)
        # self.__reply_message = None
        if call.message.text == OpationEnum.激活PikPak.value[0]:
            if call.message.message_id == self.__reply_message.message_id:
                return True
            else:
                logger.info("同一时间只能处理一个回复哦")
                return False
        elif call.message.text == OpationEnum.挂载Rclone.value[0]:
            return True

    class CustomHandler(logging.Handler):
        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        def emit(self, record):
            try:
                msg = self.format(record)
                self.callback(msg)
            except Exception:
                self.handleError(record)

    def __init__(self) -> None:
        # set_log(self.send_print_to_tg)
        handler = self.CustomHandler(self.send_print_to_tg)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger().addHandler(handler)
        for logger in loging_names:
            logger = logging.getLogger(logger)
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)

        set_captcha_callback(self.send_get_token)
        self.bot = TeleBot(telegram_api, num_threads=5)
        self.bot.register_message_handler(
            self._start_message, commands=['start'])
        self.bot.register_message_handler(
            self._交互模式, commands=['交互模式'])
        self.bot.register_message_handler(
            self._交互模式, commands=['扫描所有'])
        self.bot.register_message_handler(
            self._挂载Rclone, commands=['挂载Rclone'])
        # 交互模式 点击按钮回调
        self.bot.register_callback_query_handler(
            self.__call_back, self.__reply_button)
        self.bot.infinity_polling()


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
