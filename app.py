# !!the main entry of the program/site !! #

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
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # we imported core/db_management as "db"
        conn = db.connectDB()
        data = db.auth(conn, request.form)
        conn.close()

    if data["status"]:
        pass


@app.route("/login", methods=["GET", "POST"])
def login():
    pass


if __name__ == "__main__":
    app.run(debug=True)
