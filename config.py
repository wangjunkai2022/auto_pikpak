from read_config import get_config

mail = get_config('mail')
mail_api = mail.get("api")

invites = get_config("invites")
