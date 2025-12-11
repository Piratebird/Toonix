# !!the main entry of the program/site !! #

"""
NOTES to self

redirect -> tells the browser go to a different page
url_for("route_name") -> dynamically finds the url for the flask route [the function of the route]
"""

# ---- IMPORTS -------#

# importing the session module and redirect and other needed utilities
from flask import Flask, render_template, request, session, redirect, url_for

# importing session from flask_session to manage user_session
from flask_session import Session

# importing the database from the /core directory and assign it to db
from core import db_management as db

app = Flask(__name__)

# ---- SESSION CONFIG -------#
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "TOONIX8081"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False


# ---- ROUTES -------#
@app.route("/")
@app.route("/home")
def home_page():
    guest = request.args.get("guest")
    if guest:
        message = "You're browsing as a guest."
    elif "name" in session:
        message = f"Welcome back, {session['name']}"
    else:
        message = "Welcome! PLease login or signup :)"
    return render_template("home.html", message=message)


@app.route("/signup", methods=["GET", "POST"])
def signup():

    # check if the incoming request is POST (form submission)
    if request.method == "POST":
        # we imported core/db_management as "db"
        conn = db.connectDB()
        data = db.addUser(conn, request.form)
        conn.close()

        if data["status"]:
            # signup successful -> redirect to login page
            return redirect(url_for("login"))
        else:
            # signup failed -> show signup page with error
            return render_template("signup.html", error=data["data"])

    # GET request -> show empty signup form
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = db.connectDB()
        data = db.auth(conn, request.form)
        conn.close()

        if data["status"]:
            user = data["data"]
            # since we know name at index 1 in db -> name
            # and email at index 2 in db -> email
            session["name"] = user[1]
            session["email"] = user[2]

            # login successful -> redirect to home page
            return redirect(url_for("home_page"))
        else:
            # login failed -> show login page with error
            return render_template("login.html", error=data["data"])

    # GET request -> show empty login form
    return render_template("login.html")


@app.route("/logout")
def logout():
    pass


@app.route("/guest")
def guest_access():
    pass


if __name__ == "__main__":
    app.run(debug=True)
