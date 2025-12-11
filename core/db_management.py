# importing sqlite to deal with databse
import sqlite3

# for handeling file paths
import os


def connectDB():
    conn = sqlite3.connect("model/database.db")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users_info 
        (id integer primary key autoincrement, 
        name TEXT, 
        email TEXT, 
        password TEXT, 
        gender TEXT, 
        city TEXT)"""
    )
    return conn


def addUser(conn, data):
    try:
        cur = conn.cursor()
        data = list(data.values())
        cur.execute(
            "INSERT INTO users_info (name,email,password,gender,city) VALUES (?,?,?,?,?)",
            data,
        )
        conn.commit()
        return {"status": True, "data": "User has been added successfully."}
    except:
        return {"status": False, "data": "Something went wrong."}


def auth(conn, data):
    try:
        # 1 get the cursor so we can use it
        cur = conn.cursor()
        # 2  convert the dictionary values into list
        vals = list(data.values())
        # 3 select a user from the database
        user = cur.execute(
            "SELECT * FROM users_info WHERE email = ? AND password = ?", vals
        ).fetchone()
        ####################
        if user:
            return {"status": True, "data": user}
        else:
            return {"status": False, "data": "User not found."}
    except:
        return {"status": False, "data": "Something went wrong."}
