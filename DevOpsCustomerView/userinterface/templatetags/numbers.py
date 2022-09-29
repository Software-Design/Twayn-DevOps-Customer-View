from django.template import Library
import re

register = Library()

@register.filter()
def intval(value):
    search = re.findall(r'\d+', str(value))
    if len(search) == 0:
        return 0
    return int(search[0])

@register.filter()
def humanizeTime(time, fullDayHours=8):
    """
    Convert a time in seconds to a human readable format

    :param time: Time in seconds
    :param hours: Number of hours of a day, default is 24, false disables days
    """
    if fullDayHours:
        day = time // (fullDayHours * 3600)
        time = time % (fullDayHours * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    if fullDayHours and day > 0:
        return ("%dd %dh %dm" % (day, hour, minutes))
    if hour > 0:
        return ("%dh %dm" % (hour, minutes))
    return ("%dm" % (minutes))