import os
import telegram
from dotenv import load_dotenv
# 加载.env文件中的环境变量
load_dotenv()

TELEGRAM_KEY=os.getenv("TELEGRAM_KEY")

if __name__ == "__main__":
    if TELEGRAM_KEY and len(TELEGRAM_KEY) > 1:
        telegram.Telegram()
