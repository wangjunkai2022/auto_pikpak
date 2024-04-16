from read_config import get_config

mail = get_config('mail')
mail_api = mail.get("api")

pikpak_user = get_config("pikpak_user")

requests = get_config("requests")
requests_timeout = requests.get("out_time")
requests_retry = requests.get("retry", 0)
