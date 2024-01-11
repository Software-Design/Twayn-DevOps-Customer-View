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
    Convert a time in minutes to a human-readable format

    :param time: Time in minutes
    :param fullDayHours: Number of hours of a day, default is 8, false disables days
    """
    is_negative = False
    if time < 0:
        is_negative = True
        time = abs(time)

    if fullDayHours:
        day = time // (fullDayHours * 60)
        time = time % (fullDayHours * 60)
    hour = time // 60
    time %= 60
    minutes = time

    if is_negative:
        sign = '-'
    else:
        sign = ''

    if fullDayHours and day > 0:
        return ("%s%dd %dh %dm" % (sign, day, hour, minutes))
    if hour > 0:
        return ("%s%dh %dm" % (sign, hour, minutes))
    return ("%s%dm" % (sign, minutes))

@register.filter()
def parseHumanizedTime(time, full_day_hours=8):
    """
    Convert a duration string to minutes

    :param duration: Duration string, e.g., "1w 4d 2h 30m"
    :param full_day_hours: Number of hours of a day, default is 8, false disables days
    :return: Total duration in minutes
    """
    # Define the mapping of units to minutes
    unit_mapping = {'w': 5 * 8 * 60, 'd': 8 * 60, 'h': 60, 'm': 1}

    # Split the duration string into individual components
    components = re.findall(r'(\d+)([wdhmsWDHMS]?)', time)

    # Calculate the total duration in minutes
    total_minutes = sum(int(value) * unit_mapping.get(unit.lower(), 0) for value, unit in components)

    return total_minutes