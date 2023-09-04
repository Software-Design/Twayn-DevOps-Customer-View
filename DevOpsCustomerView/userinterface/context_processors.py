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
        'userHash': hmac.new(django_settings.VERIFICATION_SECRET, msg=args[0].user.email.encode('utf8'), digestmod=hashlib.sha256).hexdigest()
    }