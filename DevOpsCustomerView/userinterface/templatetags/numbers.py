from django.template import Library
import re

register = Library()

@register.filter()
def intval(value):
    return int(re.findall(r'\d+', str(value))[0])

@register.filter()
def humanizeTime(time):
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    if day > 0:
        return ("%dd %dh %dm" % (day, hour, minutes))
    if hour > 0:
        return ("%dh %dm" % (hour, minutes))
    return ("%dm" % (minutes))