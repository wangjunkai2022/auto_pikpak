import json
import os
import re
from tools import set_def_callback
from system_service import SystemService, SystemServiceTager
from main import ManagerAlistPikpak, change_all_pikpak, check_all_pikpak_vip as mian_run_all, 刷新PikPakToken, 所有Alist的储存库, 替换Alist储存库, 注册新号激活AlistStorage, 激活存储库vip, PiaPak保活
import enum
import io
import time
import traceback
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, Chat, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config.config
import logging

from dotenv import load_dotenv
# 加载.env文件中的环境变量
load_dotenv()

TELEGRAM_KEY=os.getenv("TELEGRAM_KEY")

# 配置日志
logging.basicConfig(
    filename='./logs.log',  # 指定日志文件名
    filemode='a',        # 'a' 表示追加模式，'w' 表示覆盖模式
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日志格式
)


logger = logging.getLogger("telegram")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

loging_names = [
    "main", "alist", "mail", "Rclone", "telegram", "system_service",
    'Chrome_Pikpak', 'PikPakSuper', "Android_pikpak",
    'captcha', '2captcha', 'captcha_chmod', 'rapidapi', 'captcha_killer', "captch_chomd",
    "proxy__index__",
]


class 模式选项(enum.Enum):
    开始 = "start"
    扫描所有 = "激活所有"
    新建所有 = "新建所有"
    选择激活 = "选择激活"
    选择替换 = "选择替换"
    选择刷新token = '选择刷新token'
    手动替换存储 = "手动替换存储"
    查看存储库的信息 = "查看存储库的信息"
    设置打印等级 = "设置打印等级"
    PK保活 = "PK保活"
    结束 = "stop"
    挂载Rclone到系统 = "挂载Rclone"
    重启系统服务 = "重启系统服务"


START_手动替换存储_STR = "_手动替换存储__"


def extract_account_and_password(log):
    """
    # 匹配账户和密码
    """
    # 使用正则表达式匹配邮箱格式
    account_pattern = r'账户:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    password_pattern = r'密码:\s*(\S+)'

    # 提取账户
    account_match = re.search(account_pattern, log)
    account = account_match.group(1) if account_match else None

    # 提取密码
    password_match = re.search(password_pattern, log)
    password = password_match.group(1) if password_match else None

    return account, password

def create_reply_keyboard(buttons, columns=2):
    """
    自动布局 ReplyKeyboardMarkup。
    
    :param buttons: 按钮文本列表
    :param columns: 每行列数
    :return: ReplyKeyboardMarkup 对象
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    
    for i, button in enumerate(buttons):
        row.append(KeyboardButton(button))
        if (i + 1) % columns == 0 or i == len(buttons) - 1:
            markup.add(*row)
            row = []
    
    return markup


class Telegram():
    bot: TeleBot = TeleBot(TELEGRAM_KEY)
    runing_chat: Chat = None
    run_temp_datas = None
    start_chat = None
    logLevel = logging.INFO

    # select手动替换存储 = {
    #     '请选择需要替换的存储库': -1,
    #     '输入新Pikpak账户': '',
    #     '输入新Pikpak密码': '',
    #     'opation_message': None
    # }
    # {"请选择需要替换的存储库": -1, },
    # {"输入新Pikpak账户": ''},
    # {"输入新Pikpak密码": ''},

    select手动替换存储 = -1
    input_email = ''
    input_pd = ''
    select_message: Message = None

    cache_json_file = os.path.abspath(__file__)[:-3] + "config" + ".json"

    conifg_userID_str = "users_ids"
    def save_config(self):
        json_data = self.read_config()
        if self.start_chat and self.start_chat.id:
            if self.start_chat.__dict__ in json_data.get(self.conifg_userID_str):
                pass
            else:
                json_data.get(self.conifg_userID_str).append(self.start_chat.__dict__)
        with open(self.cache_json_file, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(json_data, indent=4, ensure_ascii=False))
    
    def read_config(self) -> dict:
        try:
            with open(self.cache_json_file, mode="r", encoding="utf-8") as file:
                json_str = file.read()
                json_data = json.loads(json_str)
        except:
            json_data = {
                self.conifg_userID_str:[]
            }
        return json_data
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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger().addHandler(handler)
        for logger in loging_names:
            logger = logging.getLogger(logger)
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)

        self.bot.register_callback_query_handler(self.__call_back, self.__reply_button)
        self.bot.register_message_handler(self._command_handler, commands=[value.value for value in 模式选项])
        self.bot.infinity_polling()
        pass

    def _stop(self, message: Message):
        set_def_callback()
        self.send_print_to_tg("")
        self.bot.send_message(chat_id=message.chat.id, text="取消初始化 设置token的解析方式在本地默认\n如需再次Tg解析运行start即可", disable_notification=True)

    def _command_handler(self, message: Message):
        logger.debug(message)
        function_name = message.text.replace("/", "_")
        func = getattr(self, function_name, None)
        if func:
            func(message)

    def _start(self, message: Message):
        self.start_chat = message.chat
        self.save_config()
        logger.debug(message)
        self.bot.send_message(chat_id=message.chat.id, text="初始化 设置token的解析方式在tg这里", disable_notification=True)

        config.config.set_captcha_callback(self.send_get_token)
        # markup = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        for value in 模式选项:
            value = "/"+value.value
            # markup.add(KeyboardButton(value))
            buttons.append(value)
        markup = create_reply_keyboard(buttons, 5)

        self.bot.send_message(chat_id=message.chat.id, text="选择运行方式:", reply_markup=markup, disable_notification=True)

    def _设置打印等级(self, message: Message):
        self.bot.send_message(chat_id=message.chat.id, text="选择打印等级", disable_notification=True)
        levels = [logging.INFO, logging.DEBUG, logging.WARN, logging.ERROR, logging.WARNING]
        markup = InlineKeyboardMarkup(row_width=2)
        for level in levels:
            btn = InlineKeyboardButton(logging.getLevelName(level), callback_data=level,)
            markup.add(btn)
        self.bot.send_message(message.chat.id, 模式选项.设置打印等级.name, reply_markup=markup)

    def _激活所有(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(self.runing_chat.id, "你好！现在服务器开启了自动注册模式稍后会发送验证消息到你的tg请获取到token后回复验证消息", disable_notification=True)
        try:
            mian_run_all()
        except Exception as e:
            self.send_error(e)
        self._task_over()

    def _手动替换存储(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(self.runing_chat.id, "现在我们开始替换", disable_notification=True)
        try:
            self.run_temp_datas = 所有Alist的储存库()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)
        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                name = pikpak.get("name")
                statu = pikpak.get("disabled") == True and "禁用" or "启用"
                time_str = pikpak.get("update_time")
                btn = InlineKeyboardButton(f"{name} 状态:{statu} 时间:{time_str}", callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, "请选择需要替换的存储库", reply_markup=markup)

    def _重启系统服务(self, message: Message):
        self.bot.send_message(chat_id=message.chat.id, text="选择需要重启的服务 只有在root用户下执行才有效果", disable_notification=True)

        markup = InlineKeyboardMarkup(row_width=2)
        for service in SystemServiceTager:
            name_str = service.name
            btn = InlineKeyboardButton(name_str, callback_data=name_str,)
            markup.add(btn)
        # markup.add(InlineKeyboardButton(
        #     "重启服务器", callback_data="重启服务器",))
        self.bot.send_message(message.chat.id, 模式选项.重启系统服务.name, reply_markup=markup)

    def _新建所有(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(self.runing_chat.id, "你好！现在服务器开启了替换所有的pikpak", disable_notification=True)
        try:
            change_all_pikpak()
        except Exception as e:
            self.send_error(e)

        self._task_over()

    def _PK保活(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(self.runing_chat.id, "你好！现在服务器开始运行保活任务 这里是多线程 可以很快可以继续下个任务", disable_notification=True)
        try:
            PiaPak保活()
            pass
        except Exception as e:
            self.send_error(e)

        self._task_over()

    def send_error(self, e: Exception):
        self.send_print_to_tg(f"报错了{str(e)}")
        # 使用 StringIO 捕获 traceback 输出
        output = io.StringIO()
        traceback.print_exc(file=output)  # 将 traceback 输出到 StringIO
        error_message = output.getvalue()  # 获取字符串
        self.send_print_to_tg(f"track:\n{error_message}")

    def send_print_to_tg(self, message_text):
        """发送消息到TG

        Args:
            message_text (_type_): _description_
        """
        
        if self.runing_chat and self.runing_chat.id:
            chat_id = self.runing_chat.id
        elif self.start_chat and self.start_chat.id:
            chat_id = self.start_chat.id
        elif self.read_config().get(self.conifg_userID_str)[-1]:
            chat_id = self.read_config().get(self.conifg_userID_str)[-1].get("id")

        if chat_id:     
            max_length = 4096
            if len(message_text) > max_length:
                self.bot.send_message(chat_id=chat_id, text="以下是超长信息:")
                while len(message_text) > max_length:
                    # 拆分消息
                    part = message_text[:max_length]
                    self.bot.send_message(chat_id=chat_id, text=part)
                    message_text = message_text[max_length:]  # 剩余部分继续处理

            # 发送剩余部分
            if message_text:
                self.bot.send_message(chat_id=chat_id, text=message_text)        


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
        self.bot.send_message(self.runing_chat.id or self.start_chat.id, "请获取一下url的验证 并回复token到下一条消息", disable_notification=True)
        __token_message = self.bot.send_message(self.runing_chat.id or self.start_chat.id, url)
        self.bot.register_for_reply(__token_message, self.__reply_token)

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

    def _选择替换(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 所有Alist的储存库()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                name = pikpak.get("name")
                statu = pikpak.get("disabled") == True and "禁用" or "启用"
                time_str = pikpak.get("update_time")
                btn = InlineKeyboardButton(f"{name} 状态:{statu} 时间:{time_str}", callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, 模式选项.选择替换.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()

    def _选择激活(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 所有Alist的储存库()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                name = pikpak.get("name")
                statu = pikpak.get("disabled") == True and "禁用" or "启用"
                time_str = pikpak.get("update_time")
                btn = InlineKeyboardButton(f"{name} 状态:{statu} 时间:{time_str}", callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, 模式选项.选择激活.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()

    def _查看存储库的信息(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 所有Alist的储存库()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                name = pikpak.get("name")
                statu = pikpak.get("disabled") == True and "禁用" or "启用"
                time_str = pikpak.get("update_time")
                btn = InlineKeyboardButton(f"{name} 状态:{statu} 时间:{time_str}", callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, 模式选项.查看存储库的信息.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()

    def _选择刷新token(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 所有Alist的储存库()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            index = 0
            for pikpak in self.run_temp_datas:
                name = pikpak.get("name")
                statu = pikpak.get("disabled") == True and "禁用" or "启用"
                time_str = pikpak.get("update_time")
                btn = InlineKeyboardButton(
                    f"{name} 状态:{statu} 时间:{time_str}", callback_data=str(index),)
                markup.add(btn)
                index += 1
            self.bot.send_message(message.chat.id, 模式选项.选择刷新token.name,
                                  reply_markup=markup)
        else:
            self.bot.send_message(
                message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()


    def _task_over(self):
        self.bot.send_message(
            self.runing_chat.id, "任务结束。。。。。可以执行新的任务了", disable_notification=True)
        self.runing_chat = None
        self.run_temp_datas = None

    def __call_back(self, call: CallbackQuery):
        if call.data:
            if call.message.text == 模式选项.选择激活.name:
                index = int(call.data)
                pikpak = self.run_temp_datas[index]
                pikpak_name = pikpak.get("username")
                pikpak_pd = pikpak.get("password")
                storage_name = pikpak.get("name")
                self.bot.send_message(call.message.chat.id,
                                      f"正在激活中 请等待邀请的库是\n{storage_name}\n{pikpak_name}\n密码:{pikpak_pd}")
                try:
                    new_pikpak = 激活存储库vip(pikpak)
                    self.bot.send_message(call.message.chat.id,
                                          f"注册新号成功\n{new_pikpak.mail}")
                except Exception as e:
                    self.send_error(e)
                self._task_over()
            elif call.message.text == 模式选项.选择替换.name:
                index = int(call.data)
                pikpak = self.run_temp_datas[index]
                pikpak_name = pikpak.get("username")
                pikpak_pd = pikpak.get("password")
                self.bot.send_message(call.message.chat.id,
                                      f"正在注册新号中 请等待 邀请的号是\n{pikpak_name}\n密码:{pikpak_pd}")
                try:
                    new_pikpak = 注册新号激活AlistStorage(pikpak)
                    self.bot.send_message(call.message.chat.id,
                                          f"注册新号成功\n{new_pikpak.mail}")
                except Exception as e:
                    self.send_error(e)
                self._task_over()
            elif call.message.text == 模式选项.选择刷新token.name:
                index = int(call.data)
                pikpak = self.run_temp_datas[index]
                name = pikpak.get("name")
                try:
                    刷新PikPakToken(pikpak)
                    self.bot.send_message(call.message.chat.id,
                                          f"选择刷新token成功:\n{name}")
                except Exception as e:
                    self.send_error(e)
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
            elif call.message.text == "请选择需要替换的存储库":
                index = int(call.data)
                self.select手动替换存储 = index
                storage = self.run_temp_datas[self.select手动替换存储]
                name = storage.get("name")
                message = self.bot.send_message(
                    self.runing_chat.id or self.start_chat.id,
                    f'激活的存储库:{name}\n请回复以下格式的账户和密码\n账户:****\n密码:*****'
                )
                self.select_message = message
                self.bot.register_for_reply(message, self.输入新Pikpak账户和密码)
            elif call.message.text == 模式选项.查看存储库的信息.name:
                index = int(call.data)
                alistPikpak = ManagerAlistPikpak()
                storage = alistPikpak.get_storage_list().get("content")[index]
                try:
                    storage["remark"] = json.loads(storage["remark"])
                except:
                    storage["remark"] = {}
                try:
                    storage["addition"] = json.loads(storage["addition"])
                except:
                    storage["addition"] = {}
                self.bot.send_message(call.message.chat.id,
                                      f"选中的存储库的详细信息如下:\n{json.dumps(storage,ensure_ascii=False, indent=4)}")
                self._task_over()

    def 输入新Pikpak账户和密码(self, message: Message):
        user, pd = extract_account_and_password(message.text)
        if not user or user == "" or not pd or pd == "":
            message = self.bot.send_message(
                self.runing_chat.id or self.start_chat.id,
                f'输入的账户和密码有问题'
            )
        else:
            message = self.bot.send_message(
                self.runing_chat.id or self.start_chat.id,
                f'输入的账户和密码是：\n账户:{user}\n密码:{pd}'
            )
            try:
                storage = self.run_temp_datas[self.select手动替换存储]
                替换Alist储存库(user, pd, storage.get("name"))
            except Exception as e:
                self.send_error(e)
        self._task_over()

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
