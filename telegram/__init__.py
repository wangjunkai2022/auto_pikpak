import enum
import time
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, Chat, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config.config
import logging

from main import ManagerAlistPikpak, change_all_pikpak, check_all_pikpak_vip as mian_run_all, 所有的没有vip的PikPak, 注册新号激活
from system_service import SystemService, SystemServiceTager
from tools import set_def_callback

logger = logging.getLogger("telegram")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

loging_names = [
    "main", "alist", "mail", "captch_chomd", "Rclone", "telegram", "system_service", 'Chrome_Pikpak', 'PikPakSuper',
]


class 模式选项(enum.Enum):
    开始 = "start"
    扫描所有 = "激活所有"
    新建所有 = "新建所有"
    选择激活 = "选择激活"
    设置打印等级 = "设置打印等级"
    结束 = "stop"
    挂载Rclone到系统 = "挂载Rclone"
    重启系统服务 = "重启系统服务"


class Telegram():
    bot: TeleBot = TeleBot(config.config.telegram_api)
    runing_chat: Chat = None
    run_temp_datas = None
    start_chat = None
    logLevel = logging.INFO

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

    def __setLoggerLevel(self, level):
        for logger in loging_names:
            logger = logging.getLogger(logger)
            logger.setLevel(level)

    def __init__(self) -> None:
        config.config.set_captcha_callback(self.send_get_token)
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

        self.bot.register_callback_query_handler(
            self.__call_back, self.__reply_button)
        self.bot.register_message_handler(self._command_handler, commands=[
                                          value.value for value in 模式选项])
        self.bot.infinity_polling()
        pass

    def _stop(self, message: Message):
        set_def_callback()
        self.send_print_to_tg("")
        self.bot.send_message(chat_id=message.chat.id,
                              text="取消初始化 设置token的解析方式在本地默认\n如需再次Tg解析运行start即可", disable_notification=True)

    def _command_handler(self, message: Message):
        logger.debug(message)
        function_name = message.text.replace("/", "_")
        func = getattr(self, function_name, None)
        if func:
            func(message)

    def _start(self, message: Message):
        self.start_chat = message.chat
        logger.debug(message)
        self.bot.send_message(chat_id=message.chat.id,
                              text="初始化 设置token的解析方式在tg这里", disable_notification=True)

        config.config.set_captcha_callback(self.send_get_token)
        markup = ReplyKeyboardMarkup()
        for value in 模式选项:
            value = "/"+value.value
            markup.add(KeyboardButton(value))

        self.bot.send_message(chat_id=message.chat.id,
                              text="选择运行方式:", reply_markup=markup, disable_notification=True)

    def _设置打印等级(self, message: Message):
        self.bot.send_message(chat_id=message.chat.id,
                              text="选择打印等级", disable_notification=True)
        levels = [logging.INFO, logging.DEBUG,
                  logging.WARN, logging.ERROR, logging.WARNING]
        markup = InlineKeyboardMarkup(row_width=2)
        for level in levels:
            btn = InlineKeyboardButton(
                logging.getLevelName(level), callback_data=level,)
            markup.add(btn)
        self.bot.send_message(message.chat.id, 模式选项.设置打印等级.name,
                              reply_markup=markup)

    def _激活所有(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(
                message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(
            self.runing_chat.id, "你好！现在服务器开启了自动注册模式稍后会发送验证消息到你的tg请获取到token后回复验证消息", disable_notification=True)
        try:
            mian_run_all()
        except Exception as e:
            self.send_print_to_tg(e)
        self._task_over()

    def _重启系统服务(self, message: Message):
        self.bot.send_message(chat_id=message.chat.id,
                              text="选择需要重启的服务 只有在root用户下执行才有效果", disable_notification=True)

        markup = InlineKeyboardMarkup(row_width=2)
        for service in SystemServiceTager:
            name_str = service.name
            btn = InlineKeyboardButton(
                name_str, callback_data=name_str,)
            markup.add(btn)
        # markup.add(InlineKeyboardButton(
        #     "重启服务器", callback_data="重启服务器",))
        self.bot.send_message(message.chat.id, 模式选项.重启系统服务.name,
                              reply_markup=markup)

    def _新建所有(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(
                message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(
            self.runing_chat.id, "你好！现在服务器开启了替换所有的pikpak", disable_notification=True)
        try:
            change_all_pikpak()
        except Exception as e:
            self.send_print_to_tg("报错了")
            self.send_print_to_tg(e)
            self.send_print_to_tg(e.__traceback__)
        self._task_over()

    def send_print_to_tg(self, message_text):
        """发送消息到TG

        Args:
            message_text (_type_): _description_
        """
        if self.runing_chat or self.start_chat:
            self.bot.send_message(self.runing_chat.id or self.start_chat.id,
                                  message_text, disable_notification=True)

    def send_get_token(self, url: str):
        """发送验证url消息到TG TG需要回复才继续运行

        Args:
            url (str): 需要验证的url

        Returns:
            _type_: _description_
        """
        if not self.runing_chat and not self.start_chat:
            set_def_callback()
            config.config.get_captcha_callback()(url)
            # raise Exception("TG这里没有监听过 已经设置为默认的了")
            logger.error("TG这里没有监听过 已经设置为默认的了 并且回调过去了")
            return
        self.token = None
        self.bot.send_message(
            self.runing_chat.id or self.start_chat.id,
            "请获取一下url的验证 并回复token到下一条消息", disable_notification=True
        )
        __token_message = self.bot.send_message(
            self.runing_chat.id or self.start_chat.id,
            url
        )
        self.bot.register_for_reply(
            __token_message, self.__reply_token)

        # 卡线程等用户处理结果并回复token
        while not self.token:
            time.sleep(0.1)
        self.bot.clear_reply_handlers(__token_message)
        return self.token

    def __reply_token(self, message: Message):
        """用户回复token的监听

        Args:
            message (Message): 用户回复消息
        """
        captcha_token = message.text
        captcha_token = self.__find_str_token(captcha_token)
        self.token = captcha_token

    def __find_str_token(self, strs: str = "") -> str:
        """解析用户发过来的Token

        Args:
            strs (str, optional): 需要解析的字符串. Defaults to "".

        Returns:
            _type_: 解析后的字符串
        """
        str_start = "captcha_token="
        str_end = "&expires_in"
        if str_start in strs:
            strs = strs[
                strs.find(str_start)+len(str_start):
            ]
        if str_end in strs:
            strs = strs[0:strs.find(str_end)]
        return strs

    def _选择激活(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(
                message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 所有的没有vip的PikPak()
        except Exception as e:
            self.run_temp_datas = None
            self.send_print_to_tg(e)
        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                btn = InlineKeyboardButton(
                    pikpak.name, callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, 模式选项.选择激活.name,
                                  reply_markup=markup)
        else:
            self.bot.send_message(
                message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()

    def _task_over(self):
        self.bot.send_message(
            self.runing_chat.id, "任务结束。。。。。可以执行新的任务了", disable_notification=True)
        self.runing_chat = None
        self.run_temp_datas

    def __call_back(self, call: CallbackQuery):
        if call.data:
            if call.message.text == 模式选项.选择激活.name:
                index = int(call.data)
                pikpak = self.run_temp_datas[index]
                self.bot.send_message(call.message.chat.id,
                                      f"正在注册新号中 请等待 邀请的号是{pikpak.mail}")
                new_pikpak = 注册新号激活(pikpak)
                self.bot.send_message(call.message.chat.id,
                                      f"注册新号成功\n{new_pikpak.mail}")
                self._task_over()
            elif call.message.text == 模式选项.挂载Rclone到系统.name:
                # pikpak = self.rclone_manager.conifg_2_pikpak_rclone(
                #     self.rclone_manager.json_config[index])
                # alist_manager = ManagerAlistPikpak()
                # for alist in alist_manager.get_storage_list().get("content"):
                #     if alist.get("mount_path") in pikpak.mount_path:
                #         alist_manager.disable_storage(alist.get("id"))
                # pikpak.run_mount()
                self.send_print_to_tg("还在开发中。。。。。")
            elif call.message.text == 模式选项.设置打印等级.name:
                level = int(call.data)
                self.__setLoggerLevel(level)
                self.bot.send_message(chat_id=call.message.chat.id,
                                      text=f"设置打印模式{logging.getLevelName(level)}完毕", disable_notification=True)
            elif call.message.text == 模式选项.重启系统服务.name:
                if call.data == "reboot_syatem":
                    self.bot.send_message(
                        call.message.chat.id, f"重启系统中。")
                service = SystemService(SystemServiceTager[call.data])
                stop = service.stop()
                self.bot.send_message(
                    call.message.chat.id, f"停止系统{call.data}。\noutput:{stop.output}\nerror:{stop.error}")
                run = service.run()
                self.bot.send_message(
                    call.message.chat.id, f"启动系统{call.data}。\noutput:{run.output}\nerror:{run.error}")

    def __reply_button(self, call: CallbackQuery):
        if (call.message.text == 模式选项.设置打印等级.name) or (call.message.text == 模式选项.重启系统服务.name):
            return True

        if self.runing_chat and self.runing_chat.id == call.message.chat.id:
            return True
        elif self.runing_chat:
            self._task_over()


if __name__ == "__main__":
    # s = [value.value for value in 模式选项]
    # print(s)
    Telegram()
