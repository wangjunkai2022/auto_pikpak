from read_config import get_config

mail = get_config('mail')
mail_api = mail.get("api")

invites = get_config("invites")

requests = get_config("requests")
requests_timeout = requests.get("out_time")
requests_retry = requests.get("retry", 0)
