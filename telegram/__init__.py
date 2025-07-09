import json
import os
import re
from system_service import SystemService, SystemServiceTager
from main import ManagerAlistPikpak, SetDefTokenCallback, PikPakMail填写邀请码, change_all_pikpak, check_all_pikpak_vip as mian_run_all, 刷新PikPakToken, 所有Alist的储存库, 替换Alist储存库, 注册新PK账户, 注册新号激活_Pikpsk, 注册新号激活AlistStorage, 激活存储库vip, PiaPak保活, 获取pk到纸鸢数据, 获取所有PK_VIP帐号, 获取所有PK帐号, 运行某个Pikpak模拟人操作, 纸鸢数据替换本地数据
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
    "main", "alist", "mail", "mail_base", "Rclone", "telegram", "system_service",
    'Chrome_Pikpak', 'PikPakSuper', "Android_pikpak",
    'captcha', '2captcha', 'captcha_chmod', 'rapidapi', 'captcha_killer', "captch_chomd",
    "proxy__index__",
]

environs = {
    "MAIL_TYPE": f"mail 模块使用的判断获取邮箱和获取邮箱中收到的验证码 \n现在有选项 rapidapi、shanyouxiang、base",
    "TWOCAPTCHA_KEY": f"2captcha 得api 也需要先设置才能使用",
    "TELEGRAM_KEY": f"tg 机器人api 按道理这里这里不应该设置的",
    "RAPIDAPI_KEY": f"rapidapi.com api",
    "SHANYOUXIANG_KEY": f"闪邮箱API https://shanyouxiang.com/",
}

class 模式选项(enum.Enum):
    开始 = "start"
    选择PK新邀请 = "选择PK新邀请"
    选择Alist_PK新邀请 = "选择Alist_PK新邀请"
    PK保活 = "PK保活"
    选择PK执行模拟人操作 = "选择PK执行模拟人操作"
    PK转纸鸢 = "PK转纸鸢"
    纸鸢返回更新值 = "纸鸢返回更新值"
    扫描所有 = "激活所有"
    新建所有 = "新建所有"
    选择刷新token = '选择刷新token'
    手动替换存储 = "手动替换存储"
    手动输入邮箱注册新PK = "手动输入邮箱注册新PK"
    设置环境变量 = "设置环境变量"
    查看存储库的信息 = "查看存储库的信息"
    设置打印等级 = "设置打印等级"
    结束 = "stop"
    挂载Rclone到系统 = "挂载Rclone"
    重启系统服务 = "重启系统服务"

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
        SetDefTokenCallback(self.send_get_token)
        handler = self.CustomHandler(self.send_print_to_tg)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger().addHandler(handler)
        for logger in loging_names:
            logger = logging.getLogger(logger)
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)

        self.bot.register_callback_query_handler(self.__call_back, self.__reply_button)
        self.bot.register_message_handler(self._command_handler, commands=[value.value for value in 模式选项])
        self.bot.infinity_polling() #这句后面的内容不会执行 这里会永远循环
        pass

    def _stop(self, message: Message):
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

        # markup = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        for value in 模式选项:
            value = "/" + value.value
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

    def _手动输入邮箱注册新PK(self, message:Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        self.bot.send_message(self.runing_chat.id, "开始手动输入邮箱注册新PK 任务", disable_notification=True)
        class Data:
            mail = None
            code = None
            inv_code = None

        data = Data()
        def mail_get_callback():
            data.mail = None
            def reply_callback(message:Message):
                data.mail = message.text
            reply_message = self.bot.send_message(self.runing_chat.id or self.start_chat.id, f"请回复需要注册的邮箱")
            self.bot.register_for_reply(reply_message, reply_callback)
            while not data.mail:
                time.sleep(0.1)
            self.bot.clear_reply_handlers(reply_message)
            return data.mail
        
        def code_get_callback(mail=""):
            data.code = None
            def reply_callback(message:Message):
                data.code = message.text
            reply_message = self.bot.send_message(self.runing_chat.id or self.start_chat.id, f"请回复{mail}获取到的PK验证码")
            self.bot.register_for_reply(reply_message, reply_callback)
            while not data.code:
                time.sleep(0.1)
            self.bot.clear_reply_handlers(reply_message)
            return data.code
        
        pikpak = 注册新PK账户(mail_get_callback, code_get_callback)
        
        # 获得邀请码
        def inv_callback():
            data.inv_code = None
            def reply_callback(message:Message):
                data.inv_code = message.text
            reply_message = self.bot.send_message(self.runing_chat.id or self.start_chat.id, f"请输入邀请码或者需要获取邀请码的邮箱")
            self.bot.register_for_reply(reply_message, reply_callback)
            while not data.inv_code:
                time.sleep(0.1)
            self.bot.clear_reply_handlers(reply_message)
            return data.inv_code

        PikPakMail填写邀请码(pikpak.mail, inv_callback())

    def _设置环境变量(self, message: Message):
        def reply_callback(message: Message):
            txts = message.text.split()
            for env in txts:
                key, value = env.split("=")
                if key and value:
                    self.bot.send_message(message.chat.id, f"正在设置环境变量:{key}={value}")
                    os.environ[key] = value
        send_message_str = f"环境变量设置：\n可以设置的环境有:"
        for key, value in environs.items():
            send_message_str += f"\nkey:{key}\tvalue{value}"
        send_message_str += f"\n多个环境使用空格或者回车分割 健值对使用="
        send_message_str += f"\n需要回复此消息才能生效"
        reply_message = self.bot.send_message(message.chat.id, send_message_str)
        self.bot.register_for_reply(reply_message, reply_callback)

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
            # raise Exception("TG这里没有监听过 已经设置为默认的了")
            logger.error("TG这里没有监听过 已经设置为默认的了 并且回调过去了")
            return
        self.bot.send_message(self.runing_chat.id or self.start_chat.id, "请获取一下url的验证 并回复token到下一条消息", disable_notification=True)
        token_message = self.bot.send_message(self.runing_chat.id or self.start_chat.id, url)
        class Data:
            token = None
        data = Data()
        def reply(message:Message):
            captcha_token = message.text
            captcha_token = self.__find_str_token(captcha_token)
            data.token = captcha_token
            
        self.bot.register_for_reply(token_message, reply)

        # 卡线程等用户处理结果并回复token
        while not data.token:
            time.sleep(0.1)
        self.bot.clear_reply_handlers(token_message)
        self.bot.send_message(self.runing_chat.id or self.start_chat.id, f"解析后的token:{data.token}", disable_notification=True)
        return data.token

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
    
    def _选择PK新邀请(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 获取所有PK帐号()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            for pikpak in self.run_temp_datas.keys():
                btn = InlineKeyboardButton(f"{pikpak}", callback_data=pikpak,)
                markup.add(btn)

            self.bot.send_message(message.chat.id, 模式选项.选择PK新邀请.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()
    
    def _纸鸢返回更新值(self, message: Message):
        message = self.bot.send_message(message.chat.id, f'输入纸鸢返回数据')
        def reply_callback(message: Message):
            content = message.text
            纸鸢数据替换本地数据(content)
            self.bot.send_message(message.chat.id, "保存成功", disable_notification=True)
        self.bot.register_for_reply(message, reply_callback)
        
    def _PK转纸鸢(self, message: Message):
        # if self.runing_chat:
        #     self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
        #     return
        # self.runing_chat = message.chat
        try:
            self.run_temp_datas = 获取所有PK帐号()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            for pikpak in self.run_temp_datas.keys():
                btn = InlineKeyboardButton(f"{pikpak}", callback_data=pikpak,)
                markup.add(btn)

            self.bot.send_message(message.chat.id, 模式选项.PK转纸鸢.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            # self._task_over()

    def _选择PK执行模拟人操作(self, message: Message):
        if self.runing_chat:
            self.bot.send_message(message.chat.id, "你好！服务正在运行中。。。。。请等待结束在启动", disable_notification=True)
            return
        self.runing_chat = message.chat
        try:
            self.run_temp_datas = 获取所有PK帐号()
        except Exception as e:
            self.run_temp_datas = None
            self.send_error(e)

        if self.run_temp_datas and len(self.run_temp_datas) > 0:
            markup = InlineKeyboardMarkup(row_width=2)
            for pikpak in self.run_temp_datas.keys():
                btn = InlineKeyboardButton(f"{pikpak}", callback_data=pikpak,)
                markup.add(btn)

            self.bot.send_message(message.chat.id, 模式选项.选择PK执行模拟人操作.name, reply_markup=markup)
        else:
            self.bot.send_message(message.chat.id, "没有需要执行的任务", disable_notification=True)
            self._task_over()


    def _选择Alist_PK新邀请(self, message: Message):
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
            self.bot.send_message(message.chat.id, 模式选项.选择Alist_PK新邀请.name, reply_markup=markup)
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
            if call.message.text == 模式选项.选择Alist_PK新邀请.name:
                index = int(call.data)
                pikpak = self.run_temp_datas[index]
                pikpak_name = pikpak.get("username")
                pikpak_pd = pikpak.get("password")
                storage_name = pikpak.get("name")
                self.bot.send_message(call.message.chat.id,
                                      f"正在激活中 请等待邀请的库是\n{storage_name}\n{pikpak_name}\n密码:{pikpak_pd}")
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
            elif call.message.text == 模式选项.选择PK执行模拟人操作.name:
                pikpak_mail = call.data
                storage = self.run_temp_datas[pikpak_mail]
                运行某个Pikpak模拟人操作(pikpak_mail)
                self._task_over()
            elif call.message.text == 模式选项.PK转纸鸢.name:
                pikpak_mail = call.data
                storage = self.run_temp_datas[pikpak_mail]
                json_data = 获取pk到纸鸢数据(pikpak_mail)
                self.send_print_to_tg(json.dumps(json_data, indent=4, ensure_ascii=False))
                # self._task_over()
            elif call.message.text == 模式选项.选择PK新邀请.name:
                pikpak_mail = call.data
                storage = self.run_temp_datas[pikpak_mail]
                json_data = 注册新号激活_Pikpsk(pikpak_mail)
                self.send_print_to_tg(json.dumps(json_data, indent=4, ensure_ascii=False))
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
