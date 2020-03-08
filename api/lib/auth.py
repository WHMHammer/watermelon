from hashlib import sha3_512
from time import time

from info.auth import *
from lib import *

# check request entries (for database)
def legal_username(username):
    return len(username) <= username_max_length

def legal_salt(salt):
    return len(salt) == salt_length

def legal_hash(hashed):
    return len(hashed) == hash_length

def legal_email(email):
    return len(email) <= email_max_length

def legal_url(url):
    return len(url) <= url_max_length

# hash
def generate_salt():
    return rand_str(salt_length)

def hash_r(*args):
    if len(args) == 1:
        h = sha3_512(args[0])
        return h.hexdigest()
    s = args[-1]
    for i in range(len(args)-2, -1, -1):
        b = (args[i]+s).encode("utf8")
        h = sha3_512(b)
        s = h.hexdigest()
    return s

# user token
def generate_user_token(username): # username is assumed to be right. Check before calling this function!
    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT id, email, avatar
        FROM users
        WHERE username = %s
        LIMIT 1;
    """, (username,))

    user_id, email, avatar = cur.fetchone()

    session = generate_salt()
    cur.execute("""
        INSERT into sessions
        VALUES(%s, %s, %s);
    """, (user_id, session, int(time())+session_expire_time))

    flask.g.db.commit()

    return {
        "user_id": user_id,
        "session": session,
        "username": username,
        "email": email,
        "avatar": avatar
    }

def get_user_token(user_token): # user_token is a dict with exactly the same format as that of the return value of generate_user_token()
    try:
        user_id = int(user_token["user_id"])
        session = str(user_token["session"])
    except (KeyError, TypeError):
        return None

    if not legal_salt(session):
        return None

    cur  = flask.g.db.cursor()

    cur.execute("""
        DELETE from sessions
        WHERE expire_time < %s;
    """, (int(time()),))

    cur.execute("""
        SELECT users.username, users.email, users.role
        FROM users RIGHT JOIN sessions
        ON users.id=sessions.user_id
        WHERE users.id=%s AND users.status=%s AND sessions.session=%s
        LIMIT 1;
    """, (user_id, "verified", session))

    try:
        username, email, role = cur.fetchone()
    except TypeError:
        return None

    flask.g.db.commit()

    return {
        "id": user_id,
        "username": username,
        "email": email,
        "role": role
    }
