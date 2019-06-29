from lib import *

app = flask.Flask(__name__)


@app.before_request
def before_all():
    if flask.request.method == "OPTIONS":
        return "{}"
    elif flask.request.method != "GET":
        flask.g.form = flask.request.get_json()

    connect_db()

app.teardown_appcontext(close_db)


@app.after_request
def after_all(rp):
    rp.headers.set("Access-Control-Allow-Origin", "*")
    rp.headers.set("Access-Control-Allow-Methods", "OPTIONS, GET, POST, PUT, DELETE")
    rp.headers.set("Access-Control-Allow-Headers", "Content-Type")
    rp.headers.set("Content-Type", "application/json")
    return rp

from auth import bp as auth_bp
app.register_blueprint(auth_bp)

from event import bp as event_bp
app.register_blueprint(event_bp)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=80
    )
