from read_config import get_config

mail = get_config('mail')
mail_api = mail.get("api")

requests = get_config("requests")
requests_timeout = requests.get("out_time")
requests_retry = requests.get("retry", 0)

alist = get_config("alist")
alist_domain = alist.get("domain")
alist_user = alist.get("username")
alist_pd = alist.get("password")

def_password = get_config("def_password")

telegram_api = get_config("telegram").get("api", "")
