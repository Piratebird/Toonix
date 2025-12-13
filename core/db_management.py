# NOTE: [IMP!!] later on hash the password using "bcrypt"

import sqlite3
import os


def connectDB():
    """
    Connect to SQLite database. Create 'users_info' table if not exists.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users_info 
        (id integer primary key autoincrement, 
        name TEXT, 
        email TEXT, 
        password TEXT)"""
    )  # removed gender & city
    return conn


def addUser(conn, data):
    """
    Adds a new user to the database.
    Parameters:
    - conn: SQLite connection object
    - data: dictionary with keys 'name', 'email', 'password'
    Returns:
    - dictionary with 'status' (True/False) and 'data' (message)
    """
    try:
        cur = conn.cursor()

        # Only take name, email, password
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        cur.execute(
            "INSERT INTO users_info (name,email,password) VALUES (?,?,?)",
            (name, email, password),
        )
        conn.commit()
        return {"status": True, "data": "User has been added successfully."}
    except Exception as e:
        return {"status": False, "data": f"Something went wrong: {e}"}


def auth(conn, data):
    """
    Authenticates a user based on email and password.
    Parameters:
    - conn: SQLite connection object
    - data: dictionary with keys "email" and "password"
    Returns:
    - dictionary with "status" (True/False) and "data" (user info or error message)
    """
    try:
        cur = conn.cursor()
        email = data.get("email")
        password = data.get("password")

        user = cur.execute(
            "SELECT * FROM users_info WHERE email = ? AND password = ?",
            (email, password),
        ).fetchone()

        if user:
            return {"status": True, "data": user}
        else:
            return {"status": False, "data": "User not found."}
    except Exception as e:
        return {"status": False, "data": f"Something went wrong:{e}"}
