# importing sqlite to deal with databse
import sqlite3

# for handeling file paths
import os


def connectDB():
    """
    os.path.dirname(os.path.abspath(__file__)) --> ensures we get the absloue file path

    DB_PATH = os.path.join(BASE_DIR, "database.db") --> saftly join the directoy with the file

    example: os.path.join(directoy, "file.txt") --> output: directory/file.txt

    note that ? --> placeholder for values in sql
    """

    # Get the absolute path of the current script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Build the full path to the database file
    DB_PATH = os.path.join(BASE_DIR, "database.db")

    # Connect to the SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users_info 
        (id integer primary key autoincrement, 
        name TEXT, 
        email TEXT, 
        password TEXT, 
        gender TEXT, 
        city TEXT)"""
    )

    # return the connection object to be used in other functions
    return conn


def addUser(conn, data):
    """
    Adds a new user to the database.

    Parameters:
    - conn: SQLite connection object
    - data: dictionary with keys 'name', 'email', 'password', 'gender', 'city'

    Returns:
    - dictionary with 'status' (True/False) and 'data' (message)
    """

    try:
        #  create a cursor to execute sql commands
        cur = conn.cursor()

        # typecasting directoy values into a list
        data = list(data.values())

        # insert the user info into the database
        cur.execute(
            "INSERT INTO users_info (name,email,password,gender,city) VALUES (?,?,?,?,?)",
            data,
        )
        conn.commit()

        # save the changes
        return {"status": True, "data": "User has been added successfully."}
    except Exception as e:

        # catch exceptions and return a failure messsage
        return {"status": False, "data": f"Something went wrong: {e}"}


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
    except Exception as e:
        return {"status": False, "data": f"Something went wrong:{e}"}
