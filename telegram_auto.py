from config.config import telegram_api, set_log, set_captcha_callback
import telegram

if __name__ == "__main__":
    if telegram_api and len(telegram_api) > 1:
        telegram.Telegram()
