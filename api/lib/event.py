from time import time

from info.event import *
from lib import *


def check_title(title):
    return len(title) <= title_max_length


def check_description(description):
    return len(title) <= description_max_length


def check_end_time(end_time):
    return end_time > flask.g.now and end_time < flask.g.now + max_event_span


def check_weekly(schedules, window):
    if len(schedules) > weekly_schedule_max_number:
        return False

    if window < 1 or window > weekly_window_max_value:
        return False

    for i in len(schedules):
        try:
            schedules[i] = int(schedules[i])
            if schedules[i] > time_max_value:
                return False
        except TypeError:
            return False

    return True


def check_monthly(schedules, window):
    if len(schedules) > monthly_schedule_max_number:
        return False

    if window < 1 or window > monthly_window_max_value:
        return False

    for i in len(schedules):
        try:
            schedules[i] = int(schedules[i])
            if schedules[i] > time_max_value:
                return False
        except TypeError:
            return False

    return True


def rm_weekly_overlaps(schedules):
    remainders = set()
    for i in schedules:
        remainder = i % 10080    # 10080 minutes is a week
        if remainder in remainders:
            schedules.remove(i)
            continue
        remainders.add(remainder)


def rm_monthly_overlaps(schedules):
    raise NotImplementedError


def check_schedule(schedule, window, end_time):
    return schedule > flask.g.now and schedule + window < end_time


def get_attendance(event_id, user_id, start_time, end_time):
    cur = flask.g.db.cursor()
    cur.execute("""
        SELECT *
        FROM attendance
        WHERE event_id = %s AND user_id = %s AND time BETWEEN %s and %s
    """, (event_id, user_id, start_time, end_time))
    return cur.fetchall()


def add_attendance(event_id, user_id, sign_time):
    cur = flask.g.db.cursor()
    cur.execute("""
        INSERT INTO attendance
        VALUES(%s, %s, %s);
    """, (event_id, user_id, sign_time))
