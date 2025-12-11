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


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    pass


if __name__ == "__main__":
    app.run(debug=True)
