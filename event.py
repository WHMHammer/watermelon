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

@app.route("/create_event",methods=("GET","POST"))
def create_event():
    if flask.request.method=="GET":
        pass
    
    form=flask.request.get_json()

    try:
        title=str(form["title"])    
        description=str(form["description"])
        end_time=int(form["end_time"])
        weekly=tuple(form["weekly"])
        w_window=int(form["w_window"])
        monthly=tuple(form["monthly"])
        m_window=int(form["m_window"])
        #user_id
        user_id=int(form["user_id"])
        #user_id
    except (KeyError,TypeError):
        return "{}",400,{"Content-Type":"application/json"}
    
    if not(
        check_events_amount(weekly,monthly) and
        check_title(title) and
        check_description(description) and
        check_end_time(end_time) and
        check_window(w_window) and
        check_window(m_window)
    ):
        return "{}",400,{"Content-Type":"application/json"}

    weekly=remove_overlaps(weekly,w_window)
    
    conn = sqlite3.connect("watermelon.db")
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO events (title, description, end_time, weekly_window, monthly_window) VALUES (?,?,?,?,?);",
        (title,description,end_time,w_window,m_window)
        )

    c.execute(
        "SELECT seq FROM sqlite_sequence WHERE name='events';"
        )
    event_id=c.fetchone()[0]
    
    for i in range(5):
        try:
            if check_schedule(weekly[i],w_window,end_time):
                #c.execute("update events set weekly%s=date_add('1970-01-01 00:00:00',interval ? second) where id=?;",(weekly[i],event_id))    # mysql
                c.execute("update events set weekly%d=datetime(?,'unixepoch') where id=?;"%(i),(weekly[i],event_id))
            else:
                conn.close()
                return "{}",400,{"Content-Type":"application/json"}
        except IndexError:
            break
    
    for i in range(1):
        try:
            if check_schedule(monthly[i],m_window,end_time):
                #c.execute("update events set monthly%s=date_add('1970-01-01 00:00:00',interval ? second where id=?);",(monthly[i],event_id))    # mysql
                c.execute("update events set monthly%d=datetime(?,'unixepoch') where id=?;"%(i),(monthly[i],event_id))
            else:
                conn.close()
                return "{}",400,{"Content-Type":"application/json"}
        except IndexError:
            break
    
    c.execute("INSERT into roles values(?,?,?);",(event_id,user_id,"owner"))
    
    conn.commit()
    conn.close()
    return "{}",{"Content-Type":"application/json"}
    # 等效于 return "{}",200,{"Content-Type":"application/json"}
    # 200 status code已能说明成功存储

def check_title(title):
    return len(title)<33

def check_description(description):
    return len(description)<129

def check_end_time(end_time):
    cur_time=int(time())
    return end_time>cur_time and end_time<cur_time+8640000

def check_window(window):
    return window>0 and window<1000

def check_schedule(schedule,window,end_time):
    cur_time=int(time())
    return schedule>cur_time and schedule+window<end_time

def check_events_amount(weekly,monthly):
    return len(weekly)<=5 and len(monthly)<=1

def remove_overlaps(weekly,w_window):
    check=()
    for i in range (len(weekly)):
        remainder=(weekly[i]%604800)//(w_window*60)
        if not (remainder in check):
            check.add(remainder)
        else:
            del weekly[i]
    return weekly