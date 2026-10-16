from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3

# ================= BLUEPRINT ================= #

auth_api = Blueprint(
    "auth_api",
    __name__
)

# ================= DATABASE ================= #

DB_FILE = "database/users.db"

# ================= CREATE TABLE ================= #

def create_users_table():

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fullname TEXT,

            username TEXT UNIQUE,

            email TEXT UNIQUE,

            password TEXT
        )

    ''')

    conn.commit()

    conn.close()

# Create DB table automatically
create_users_table()

# ================= REGISTER ================= #

@auth_api.route(
    "/register",
    methods=["GET", "POST"]
)

def register():

    if request.method == "POST":

        fullname = request.form["fullname"]

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        confirm_password = request.form[
            "confirm_password"
        ]

        if password != confirm_password:

            return "Passwords do not match"

        hashed_password = generate_password_hash(
            password
        )

        conn = sqlite3.connect(DB_FILE)

        cursor = conn.cursor()

        try:

            cursor.execute(

                '''
                INSERT INTO users(
                    fullname,
                    username,
                    email,
                    password
                )

                VALUES (?, ?, ?, ?)
                ''',

                (
                    fullname,
                    username,
                    email,
                    hashed_password
                )
            )

            conn.commit()

        except Exception as e:

            return f"Error: {e}"

        finally:

            conn.close()

        return redirect("/login")

    return render_template(
        "register.html"
    )

# ================= LOGIN ================= #

@auth_api.route(
    "/login",
    methods=["GET", "POST"]
)

def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = sqlite3.connect(DB_FILE)

        cursor = conn.cursor()

        cursor.execute(

            '''
            SELECT *
            FROM users
            WHERE username=?
            ''',

            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            stored_password = user[4]

            if check_password_hash(
                stored_password,
                password
            ):

                session["user"] = username

                return redirect("/")

        return "Invalid Username or Password"

    return render_template(
        "login.html"
    )

# ================= FORGOT PASSWORD ================= #

@auth_api.route(
    "/forgot-password",
    methods=["GET", "POST"]
)

def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        new_password = "admin123"

        hashed_password = generate_password_hash(
            new_password
        )

        conn = sqlite3.connect(DB_FILE)

        cursor = conn.cursor()

        cursor.execute(

            '''
            UPDATE users
            SET password=?
            WHERE email=?
            ''',

            (
                hashed_password,
                email
            )
        )

        conn.commit()

        conn.close()

        return '''
        Password reset successful.

        Temporary password:
        admin123
        '''

    return render_template(
        "forgot_password.html"
    )

# ================= LOGOUT ================= #

@auth_api.route("/logout")

def logout():

    session.clear()

    return redirect("/login")