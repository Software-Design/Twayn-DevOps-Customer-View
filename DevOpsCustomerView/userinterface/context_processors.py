from django.conf import settings as django_settings
import datetime
import hashlib
import hmac

def settings(*args) -> dict:
    """
    Sets some default "environment variables" and returns them
    """

    return {
        'settings': django_settings,
        'now': datetime.datetime.today,
        'base': django_settings.TEMPLATE+'/base.html',
        'userHash': hmac.new(bytes(django_settings.VERIFICATION_SECRET,'utf-8'), msg=args[0].user.email.encode('utf8'), digestmod=hashlib.sha256).hexdigest() if args[0].user.is_authenticated else None
    }