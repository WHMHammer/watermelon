from flask import Flask, request
import sqlite3

app=Flask(__name__)

@app.route("/create_event",methods=["POST"])
def create_event():
    #check input validation
    try:
        if request.method != "POST":
            e_message="405, Methods not Allowed"
            return e_message
        #check events amount
        elif len(request.form["weekly"]) > 5:
            e_message="400, Bad Request"
            return e_message
        elif len(request.form["monthly"]) > 1:
            e_message="400, Bad Request"
            return e_message

        #insert to data table
        else:
            insert_to_table(request.form)
            return "event recorded"

    except KeyError:
            e_message="400, Bad Request"
            return e_message

    def insert_to_table(form):
        event_name = form["name"]
        description = form["description"]
        end_time = form["end_time"]
        weekly = form["weekly"]

        conn = sqlite3.connect("watermelon.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO events (name, description, end_time) VALUES (?,?,?)",
            (event_name,description,end_time,)
            )
        for i in range(len(weekly)):
            c.execute(
                "INSERT INTO events (weekly_?_begin, weekly_?_end) VALUES (weekly[?])",(i,i,i)
                )
        try:
            monthly = form["monthly"]
        except KeyError:
            monthly = ["",""]
        c.execute(
            "INSERT INTO events (monthly_0_begin,monthly_0_end) VALUES (?)",(monthly)
            )

        conn.commit()
        conn.close()