from simplejson import dumps
from time import time

from lib import *
from lib.event import *
from lib.auth import get_user_token

bp = flask.Blueprint("event", __name__, url_prefix="/event")


@bp.before_request
def before_event():
    flask.g.now = int(time()) // 60
    if flask.request.method != "GET":
        flask.g.user = get_user_token()
        if flask.g.user is None:
            return "{}", 403


@bp.route("/events", methods=("POST",))
def create_event():
    try:
        title = str(flask.g.form["title"])    
        description = str(flask.g.form["description"])
        end_time = int(flask.g.form["end_time"])
        weekly_schedules = list(flask.g.form["weekly_schedules"])
        weekly_window = int(flask.g.form["weekly_window"])
        monthly_schedules = list(flask.g.form["monthly_schedules"])
        monthly_window = int(flask.g.form["monthly_window"])
    except (KeyError,TypeError):
        return "{}", 400

    if not(
        check_title(title) and
        check_description(description) and
        check_end_time(end_time) and
        check_weekly(weekly_schedules, weekly_window) and
        check_monthly(monthly_schedules, monthly_window)
    ):
        return "{}", 400

    rm_weekly_overlaps(weekly_schedules)

    cur = flask.g.db.cursor()

    cur.execute("""
            INSERT INTO events(title, description, end_time, weekly_window, monthly_window)
            VALUES (?,?,?,?,?);
        """, (title, description, end_time, weekly_window, monthly_window))

    cur.execute("SELECT LAST_INSERT_ID();")
    event_id = cur.fetchone()[0]

    for i in range(weekly_schedule_max_number):
        try:
            if check_schedule(weekly_schedules[i], weekly_window, end_time):
                cur.execute("""
                    UPDATE events
                    SET weekly%d = %s
                    WHERE id = %s;
                """ % i, (weekly_schedules[i], event_id))
            else:
                return "{}", 403
        except IndexError:
            break

    for i in range(monthly_schedule_max_number):
        try:
            if check_schedule(monthly_schedules[i], monthly_window, end_time):
                cur.execute("""
                    UPDATE events
                    SET monthly%d = FROM_UNIXTIME(%s)
                    WHERE id = %s;
                """ % i, (monthly_schedules[i], event_id))
            else:
                return "{}", 403
        except IndexError:
            break

    cur.execute("""
        INSERT INTO roles
        VALUES(%s,%s,%s);
    """, (event_id, flask.g.user["id"], "owner"))

    flask.g.db.commit()

    return "{}"


@bp.route("/attendance", methods=("POST",))
def sign_attendance():
    form = flask.request.get_json()

    try:
        event_id = int(form["event_id"])
        response = str(form["response"])
    except (KeyError,TypeError):
        return "{}", 400

    cur = flask.g.db.cursor()

    # check whether user is a subscriber
    cur.execute("""
        SELECT *
        FROM roles
        WHERE event_id = %s AND user_id = %s AND role = %s
        LIMIT 1;
    """, (event_id, flask.g.user["id"], "subscriber"))
    if cur.fetchone() is None:
        return dumps({"err_msg": ["You have not subscribed this event."]}), 403

    # check whether event has ended
    cur.execute("""
        SELECT end_time, weekly_window, monthly_window
        FROM events
        WHERE id = %s;
    """, (event_id,))
    end_time, weekly_window, monthly_window = cur.fetchone()

    if flask.g.now >= end_time:
        return dumps({"err_msg": ["Event has ended."]}), 403

    # check time
    for i in range(weekly_schedule_max_number):
        cur.execute(f"""
            SELECT weekly{i}
            FROM events
            WHERE id = %s
            LIMIT 1;
        """, (event_id,))
        try:
            schedule = cur.fetchone()[0]
        except IndexError:
            break

        while flask.g.now >= schedule and flask.g.now <= end_time:
            if flask.g.now <= schedule + weekly_window:
                add_attendance(event_id, flask.g.user["id"], flask.g.now)
                flask.g.db.commit()
                return "{}"

            cur.execute(f"""
                UPDATE events
                SET weekly{i} = (
                    SELECT weekly{i}
                    FROM events
                    WHERE id = %s
                ) + 10080   /* 10080 minutes is a week */
                WHERE id = %s;
            """, (event_id, event_id))

    for i in range(monthly_schedule_max_number):
        cur.execute(f"""
            SELECT monthly{i}
            FROM events
            WHERE id = %s
            LIMIT 1;
        """, (event_id,))
        try:
            schedule = cur.fetchone()[0]
        except IndexError:
            break

        while flask.g.now >= schedule and flask.g.now <= end_time:
            if flask.g.now <= schedule + monthly_window:
                add_attendance(event_id, flask.g.user["id"], flask.g.now)
                flask.g.db.commit()

                return "{}"

            cur.execute(f"""
                UPDATE events
                SET monthly{i} = UNIX_TIMESTAMP(
                    DATEADD(
                        FROM_UNIXTIME((
                            SELECT monthly{i}
                            FROM events
                            WHERE id = %s
                        ) * 60),
                        INTERVAL 1 MONTH
                    )
                ) DIV 60
                WHERE id = %s;
            """, (event_id, event_id))

    # check response
    # not implemented yet

    flask.g.db.commit()

    return "{}"
