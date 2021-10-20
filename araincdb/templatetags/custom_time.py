from django import template
import calendar
from datetime import datetime
import datetime

register = template.Library()


@register.filter(name='secondsToHHMMSS')
def seconds_to_hhmmss(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)


@register.filter(name='hours_to_seconds')
def hours_to_seconds(hours):
    hours = hours.split(":")
    seconds = float(hours[2]*360) + float(hours[1]*60) + float(hours[0])
    return seconds


@register.filter(name='month_name')
def month_name(month_number):
    return calendar.month_name[month_number]


@register.filter(name='age')
def age(bday, d=None):
    bday = datetime.strptime(bday, '%Y-%m-%d')
    if d is None:
        d = datetime.date.today()
    return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))


@register.filter(name='add_days')
def add_days(days):
   newDate = datetime.date.today() + datetime.timedelta(days=days)
   return newDate