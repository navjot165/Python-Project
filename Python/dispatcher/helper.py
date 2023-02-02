from routes.models import *
import datetime


def GetScheduleWeekDays(schedule):
    # Mon, tues, Wed, Thurs, Fri, Sat, Sun = 0,1,2,3,4,5,6
    week_days = []
    if schedule.monday:
        week_days.append(0)
    if schedule.tuesday:
        week_days.append(1)
    if schedule.wednesday:
        week_days.append(2)
    if schedule.thursday:
        week_days.append(3)
    if schedule.friday:
        week_days.append(4)
    if schedule.saturday:
        week_days.append(5)
    if schedule.sunday:
        week_days.append(6)
    return week_days