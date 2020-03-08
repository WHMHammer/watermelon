from time import time
from urllib.parse import unquote

from lib.auth import *

bp = flask.Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("POST",))
def register():
    try:
        username = str(flask.g.form["username"])
        salt = str(flask.g.form["salt"])
        password_hash = str(flask.g.form["password_hash"])
        email = str(flask.g.form["email"]).lower()
    except (KeyError, TypeError):
        return "{}", 400

    if (
        not legal_username(username) or
        not legal_salt(salt) or
        not legal_hash(password_hash) or
        not legal_email(email)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    err = False
    err_msg = list()

    cur.execute("""
        SELECT *
        FROM users
        WHERE email = %s AND status != %s
        LIMIT 1;
    """, (email, "unverified"))

    if cur.fetchone() is not None:
        err = True
        err_msg.append(E_email_registered)

    cur.execute("""
        SELECT *
        FROM users
        WHERE username = %s AND status != %s
        LIMIT 1;
    """, (username, "unverified"))

    if cur.fetchone() is not None:
        err = True
        err_msg.append(E_username_registered)

    if err:
        return dumps({"err_msg": err_msg}), 403

    challenge = generate_salt()

    cur.execute("""
        DELETE FROM users
        WHERE username = %s OR email = %s;
    """, (username, email))

    cur.execute("""
        INSERT INTO users(username, email, salt, password_hash, challenge)
        VALUES(%s, %s, %s, %s, %s);
    """, (username, email, salt, password_hash, challenge))

    try:
        verify_url = f"{domain}/auth/verify"
        send_email(
            noreply,
            email,
            f"Verify your registration at {project_name}",
            f"""
                <p>Hello, dear {username}:</p>
                <p>Your verification code is:</p>
                <p><code>{challenge+salt}</code></p>
                <p>Please click <a href="{verify_url}">here</a> or paste the following url to your web browser to verify your registration:</p>
                <p>{verify_url}</p>
                <br/>
                <p>Best regards,</p>
                <p>{project_name}</p>
            """
        )
    except smtplib.SMTPRecipientsRefused:
        return dumps({
            "err_msg": [E_invalid_email]}
        ), 403

    flask.g.db.commit()

    return "{}"

@bp.route("/register", methods=("PUT",))
def verify():
    try:
        username = str(flask.g.form["username"])
        response = str(flask.g.form["response"])
        email = str(flask.g.form["email"]).lower()
    except (KeyError, TypeError):
        return "{}", 400

    if not(
        legal_username(username) and
        legal_hash(response) and
        legal_email(email)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT password_hash, challenge
        FROM users
        WHERE username = %s AND email = %s AND status = %s
        LIMIT 1;
    """, (username, email, "unverified"))

    try:
        password_hash, challenge = cur.fetchone()
    except TypeError:
        return "{}", 403

    if response != hash_r(challenge, password_hash):
        return "{}", 403

    cur.execute("""
        UPDATE users
        SET status = %s, challenge = %s
        WHERE username = %s;
    """, ("verified", generate_salt(), username))

    send_email(
        noreply,
        email,
        f"Your registration at {project_name} is verified",
        f"""
            <p>Dear {username}:</p>
            <p>Your registration at {project_name} is verified. Have fun!</p>
            <br/>
            <p>Best regards,</p>
            <p>{project_name}</p>
        """
    )

    flask.g.db.commit()

    return dumps({
        "user_token": generate_user_token(username)
    })

@bp.route("/login", methods=("GET",))
def get_challenge():
    try:
        username = unquote(str(flask.g.form["username"]))
    except (KeyError, TypeError):
        return "{}", 400

    if not(
        legal_username(username)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT salt
        FROM users
        WHERE username = %s AND status = %s
        LIMIT 1;
    """, (username, "verified"))

    try:
        salt = cur.fetchone()[0]
    except TypeError:
        
        return "{}", 404

    challenge = generate_salt()

    cur.execute("""
        UPDATE users
        SET challenge = %s
        WHERE username = %s;
    """, (challenge, username))

    flask.g.db.commit()

    return dumps({
        "salt": salt,
        "challenge": challenge
    })

@bp.route("/login", methods=("POST",))
def login():
    try:
        username = str(flask.g.form["username"])
        response = str(flask.g.form["response"])
    except (KeyError, TypeError):
        return "{}", 400

    if not(
        legal_username(username) and
        legal_hash(response)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT password_hash, challenge
        FROM users
        WHERE username = %s AND status = %s
        LIMIT 1;
    """, (username, "verified"))
    try:
        password_hash, challenge = cur.fetchone()
    except TypeError:
        return "{}", 403

    if response != hash_r(challenge, password_hash):
        return "{}", 403

    cur.execute("""
        UPDATE users
        SET challenge = %s
        WHERE username = %s;
    """, (generate_salt(), username))

    flask.g.db.commit()

    return dumps({
        "user_token": generate_user_token(username)
    })

@bp.route("/login", methods=("DELETE",))
def logout():
    user = get_user_token(flask.g.form.get("user_token", None))

    if user is None:
        return "{}"

    cur = flask.g.db.cursor()

    cur.execute("""
        DELETE FROM sessions
        WHERE user_id = %s AND session = %s;
    """, (user["id"], flask.request.get_json().get("user_token")["session"]))

    flask.g.db.commit()

    return "{}"

@bp.route("/password", methods=("GET",))
def request_password_reset():
    try:
        email = unquote(str(flask.g.form["email"]))
    except (KeyError, TypeError):
        return "{}", 400

    if not legal_email(email):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT id, username
        FROM users
        WHERE email = %s AND status=%s
        LIMIT 1;
    """, (email, "verified"))

    try:
        user_id, username = cur.fetchone()
    except TypeError:
        return "{}"

    challenge = rand_str(32)

    cur.execute("""
        UPDATE users
        SET status = %s
        WHERE id = %s;
    """, (challenge, user_id))

    cur.execute("""
        DELETE FROM sessions
        WHERE user_id = %s;
    """, (user_id,))

    flask.g.db.commit()

    reset_password_url = f"{domain}/auth/reset_password"
    send_email(
        noreply,
        email,
        f"Reset your password at {project_name}",
        f"""
            <p>Hello, dear {username}:</p>
            <p>Your verification code is:</p>
            <p><code>{challenge}</code></p>
            <p>Please click <a href="{reset_password_url}">here</a> or paste the following url to your web browser to reset your password:</p>
            <p>{reset_password_url}</p>
            <br/>
            <p>Best regards,</p>
            <p>{project_name}</p>
        """
    )

    return "{}"

@bp.route("/password", methods=("PUT",))
def reset_password():
    try:
        username = str(flask.g.form["username"])
        email = str(flask.g.form["email"]).lower()
        response = str(flask.g.form["response"])
        salt = str(flask.g.form["salt"])
        password_hash = str(flask.g.form["password_hash"])
    except (KeyError, TypeError):
        return "{}", 400

    if not(
        legal_username(username) and
        legal_email(email) and
        len(response) == 32 and
        legal_salt(salt) and
        legal_hash(password_hash)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT *
        FROM users
        WHERE username = %s AND email = %s AND status = %s
        LIMIT 1;
    """, (username, email, response))

    if cur.fetchone() is None:
        return "{}", 403

    cur.execute("""
        UPDATE users
        SET status = %s, salt = %s, password_hash = %s
        WHERE username=%s;
    """, ("verified", salt, password_hash, username))

    flask.g.db.commit()

    send_email(
        noreply,
        email,
        "You have successfully changed your password!",
        f"""
            <p>Hello, dear {username}:</p>
            <p>You have successfully changed your password!</p>
            <br/>
            <p>Best regards,</p>
            <p>{project_name}</p>
        """
    )

    return dumps({
        "user_token": generate_user_token(username)
    })

@bp.route("/user", methods=("GET",))
def get_username():
    try:
        email = unquote(str(flask.g.form["email"]))
    except (KeyError, TypeError):
        return "{}", 400

    if not(
        legal_email(email)
    ):
        return "{}", 400

    cur = flask.g.db.cursor()

    cur.execute("""
        SELECT username
        FROM users
        WHERE email = %s AND status = %s
        LIMIT 1;
    """, (email, "verified"))

    try:
        username = cur.fetchone()[0]
    except TypeError:
        pass
    else:
        send_email(
            noreply,
            email,
            f"Your username at {project_name}",
            f"""
                <p>Your username at {project_name} is:</p>
                <p>{username}</p>
                <br/>
                <p>Best regards,</p>
                <p>{project_name}</p>
            """
        )

    return "{}"

@bp.route("/user", methods=("PUT",))
def update_user_info():
    user = get_user_token(flask.g.form.get("user_token", None))

    if user is None:
        return "{}", 401

    cur = flask.g.db.cursor()

    if "username" in flask.g.form:
        username = str(flask.g.form["username"])
        if not legal_username(username):
            return "{}", 400

        cur.execute("""
            UPDATE users
            SET username = %s
            WHERE id = %s;
        """, (username, user["user_id"]))

    if "email" in flask.g.form:
        email = str(flask.g.form["email"])
        if not legal_email(email):
            return "{}", 400

        cur.execute("""
            UPDATE users
            SET email = %s
            WHERE id = %s;
        """, (email, user["user_id"]))

    if "avatar" in flask.g.form:
        avatar = str(flask.g.form["avatar"])
        if not legal_url(avatar):
            return "{}", 400

        cur.execute("""
            UPDATE users
            SET avatar = %s
            WHERE id = %s;
        """, (avatar, user["user_id"]))

    if "password_hash" in flask.g.form:
        try:
            salt = str(flask.g.form["salt"])
            password_hash = str(flask.g.form["password_hash"])
        except (KeyError, TypeError):
            return "{}", 400

        if not(
            legal_salt(salt) and
            legal_hash(password_hash)
        ):
            return "{}", 400

        cur.execute("""
            UPDATE users
            SET salt = %s, password_hash = %s
            WHERE id = %s;
        """, (salt, password_hash, user["user_id"]))

    flask.g.db.commit()

    return "{}"

@bp.route("/user", methods=("DELETE",))
def delete_user():
    user = get_user_token(flask.g.form.get("user_token", None))

    if user is None:
        return "{}"

    cur = flask.g.db.cursor()

    cur.execute("""
        DELETE FROM sessions
        WHERE user_id = %s;
    """, (user["user_id"],))

    cur.execute("""
        DELETE FROM users
        WHERE user_id = %s;
    """, (user["user_id"],))

    flask.g.db.commit()

    return "{}"
