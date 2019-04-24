import flask    
from time import time
import sqlite3

app=flask.Flask(__name__)

@app.route("/create_event",methods=("GET","POST"))
def create_event():
    if flask.request.method=="GET":
        pass
    
    form=flask.request.get_json()

    try:
        title=str(form["title"])    
        description=str(form["description"])
        end_time=int(form["end_time"])
        weekly=tuple(form["weekly"]),
        w_window=int(form["w_window"]),
        monthly=tuple(form["monthly"]),
        m_window=tuple(form["m_window"])
        #user_id
        user_id=int(form["user_id"])
        #user_id
    except (KeyError,TypeError):
        return "{}",400,{"Content-Type":"application/json"}
    
    if not(
        check_title(title) and
        check_description(description) and
        check_end_time(end_time) and
        check_window(w_window) and
        check_window(m_window)
    ):
        return "{}",400,{"Content-Type":"application/json"}
    
    conn = sqlite3.connect("watermelon.db")
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO events (title, description, end_time, weekly_window, monthly_window) VALUES (?,?,?,?,?);",
        (title,description,end_time,w_window,m_window)
        )

    c.execute(
        "SELECT seq FROM sqlite_sequence WHERE name='events';"
        ))
    event_id=c.fetchone()[0]
    
    for i in range(5):
        try:
            if check_schedule(weekly[i],w_window,end_time):
                #c.execute("update events set weekly%s=date_add('1970-01-01 00:00:00',interval ? second) where id=?;",(weekly[i],event_id))    # mysql
                c.execute("update events set weekly%s=datetime('1970-01-01 00:00:00',?) where id=?;",("+%d second"%weekly[i],event_id))    # sqlite3
            else:
                conn.close()
                return "{}",400,{"Content-Type":"application/json"}
        except IndexError:
            break
    
    for i in range(1):
        try:
            if check_schedule(monthly[i],m_window,end_time):
                #c.execute("update events set monthly%s=date_add('1970-01-01 00:00:00',interval ? second where id=?);",(monthly[i],event_id))    # mysql
                c.execute("update events set monthly%s=datetime('1970-01-01 00:00:00',?) where id=?;",("+%d second"%monthly[i],event_id))    # sqlite3
            else:
                onn.close()
                return "{}",400,{"Content-Type":"application/json"}
        except IndexError:
            break
    
    c.execute("INSERT into roles values(?,?,?);",(event_id,user_id,"owner"))
    
    conn.commit()
    conn.close()
    return "{}",{"Content-Type":"application/json"}

def check_title(title):
    return len(title)<33

def check_description(description):
    return len(description)<129

def check_end_time(end_time):
    cur_time=int(time())
    return end_time>cur_time and end_time<cur_time+8640000

def check_window(window):
    return window>0 and window<1000

def check_schedule(schedule,window):
    cur_time=int(time())
    return schedule>cur_time and schedule+window<end_time
