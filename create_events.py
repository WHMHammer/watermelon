from flask import Flask, request
import time
import datetime
import sqlite3

app=Flask(__name__)

@app.route("/create_event",methods=["POST"])
def create_event():

    form=flask.request.get_json()

    #check input validation
    try:
        event_name = form["name"]
        description = form["description"]
        end_time = form["end_time"]
        window=form["window"]
        weekly=[]

        for i in form["weekly"]:
            weekly.append(datetime.fromtimestamp(i))
            waiting=i-time.time()
            if waiting>60*60*24*100:
                return "{}",400,{"Content-Type":"application/json"}
        try:
        monthly= datetime.fromtimestamp(form["monthly"])
        if form["monthly"]-time.time()>60*60*24*100:
            return "{}",400,{"Content-Type":"application/json"}
        except KeyError:
            monthly=[None]

        elif len(weekly)>5 or len(monthly)>1 or len(str(window))>3:
            return "{}",400,{"Content-Type":"application/json"}

    except KeyError:
        return "{}",400,{"Content-Type":"application/json"}
    except ValueError:
        return "{}",400,{"Content-Type":"application/json"}

    #insert to data table
    conn = sqlite3.connect("watermelon.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO events (name, description, end_time, window) VALUES (?,?,?,?)",
        (event_name,description,end_time,window,)
        )
    c.execute(
        "INSERT INTO events (monthly_0_begin) VALUES (?)",
        monthly
        )

    for i in range(len(weekly)):
        c.execute(
            "INSERT INTO events (weekly_?_begin) VALUES (?)",
            (i,weekly[i])
            )

    conn.commit()
    conn.close()
    return {"event created"},,{"Content-Type":"application/json"}
