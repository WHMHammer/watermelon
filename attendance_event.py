import flask    
from time import time
import sqlite3
from lib.auth import check_user_token

app=flask.Flask(__name__)

@app.route("/attendance_event",method=("GET","POST"))
def sign_in():
    if flask.request.method=="GET":
        pass

    form=flask.request.get_json()

    try:
        user_token=check_user_token()
        event_id=int(form["event_id"])
        verification=str(form["verification"])
    except (KeyError,TypeError):
        return "{}",400,{"Content-Type":"application/json"}

    conn=sqlite3.connect("watermelon.db")
    c=conn.cursor()

    now=int(time())
    c.execute(
        "SELECT end_time, weekly_window, monthly_window from events WHERE id=?;",
        (event_id)
        )
    data=fetchone()
    end_time=data[0]
    w_window=data[1]
    m_window=data[2]

    if now >= end_time:
    return "{}",400,{"Content-Type":"application/json"}

    if not(
        verify_subscription() and
        verify_code(verification) and
        verify_time(now,end_time,w_window,m_window,event_id,user_token["id"])
    ):
        return "{}",400,{"Content-Type":"application/json"}

    c.execute(
        "INSERT INTO attendance (event_id,user_id) VALUES (?,?);",
        (event_id,user_token["id"])
        )

    conn.commit()
    c.close()
    conn.close()
    return "{}",{"Content-Type":"application/json"}

def subscription()：
    c.execute(
        "SELECT role from roles WHERE event_id=? AND user_id=?;",
        (event_id，user_token["id"])
        )
    record=c.fetchone()

    if record[0]=="subscriber":
        return True
    else:
        return "{}",400,{"Content-Type":"application/json"}

def verify_code():
    return True

def verify_time(now,end_time,w_window,m_window,event_id,user_id):
    c.execute(
        "SELECT weekly0,weekly1,weekly2,weekly3,weekly4 from events WHERE id=?;",
        (event_id)
        )
    w_start=tuple(fetchone())

    for i in w_start:
        if now<i:
            continue
        else:
            if now<(i+w_window):
                return verify_previous_sign(i,w_window,event_id,user_id)
            else:
                if i+604800>=end_time:
                    continue
                else:
                    e.execute(
                        "UPDATE events set weekly?%d=datetime(?,'unixepoch') WHERE id=?;",
                        (w_start.index(i),i+604800,)
                        )
                    verify_time(now,end_time,w_window,m_window,event_id,user_id)

    c.execute(
        "SELECT monthly0 from events WHERE id=?;",
        (event_id)
        )
    m_start=tuple(fetchone())

    if now>m_start[0] and now<(m_start[0]+m_window):
        return verify_previous_sign(m_start[0],m_window,event_id,user_id)
    elif now>(m_start[0]+m_window) and m_start[0]+604800<end_time:
        e.execute(
                "UPDATE events set monthly0%d=datetime(?,'unixepoch') WHERE id=?;",
                (m_start[0]+604800,event_id)
                )
        verify_time(now,end_time,w_window,m_window,event_id,user_id)

    return False

def verify_previous_sign(start,window event_id,user_id):
    c.execute(
        "SELECT * from attendance where event_id=? and user_id=? and time between (?) and (?);",
        (event_id, user_id, start, start+window)
        )
    data=fetchall()
    if data == None:
        return True