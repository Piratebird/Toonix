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
from core import api

# ---- SESSION CONFIG -------#
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
""" 
in real world application this is bad ,
but in my case this can be modified later on esp since don't send data or anything 
best practice either auto generate or .env
"""
app.secret_key = "TOONIX8081"
app.config["SESSION_TYPE"] = "filesystem"  # store session on server filesystem
Session(app)  # initialize Flask-Session
app.config["SESSION_PERMANENT"] = False


# ---- ROUTES -------#
@app.route("/")
def intro_page():
    return render_template("intro.html")


@app.route("/home")
def home_page():
    name = session.get("name")
    guest = request.args.get("guest")

    if guest:
        message = "You're browsing as a guest."

    elif "name" in session:
        message = f"Welcome back, {name}!"
    else:
        message = "Welcome to Toonix :)"

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
            return render_template("home.html", error=data["data"])

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
            session["user"] = {"name": user[1], "email": user[2]}

            # login successful -> redirect to home page
            return redirect(url_for("home_page"))
        else:
            # login failed -> show login page with error
            return render_template("home.html", error=data["data"])

    # GET request -> show empty login form
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("intro_page"))


@app.route("/guest")
def guest_access():
    # mark user as a guest in the session
    session["name"] = "Guest"
    session["email"] = None  # no email for guests

    # redirect to home page with a query parameter to show guest message
    return redirect(url_for("home_page", guest=1))


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    results -> empty list to store manga search results
    query -> empty string to store the search query from the user
    """
    results = []
    query = ""

    # check if the submitted msg is post
    if request.method == "POST":
        # request.form -> a dic of data submitted from the html form
        # .get(query) -> fetch the user's query or wtv
        query = request.form.get("query")
        if query:
            # call core/api.py search function
            results = api.search_manga(query)
    # results = results -> pass the search results to the template
    # query = query -> pass the search term to the template
    return render_template("search.html", results=results, query=query)


@app.route("/manga/<manga_id>")
def view_manga(manga_id):
    """
    fetch metadata and cover and chapter list
    """
    manga = api.fetch_manga_local(manga_id)
    if not manga:
        return "Manga not found :(", 404

    cover = api.get_manga_cover(manga)
    chapters = api.get_manga_chapters(manga_id)

    return render_template("manga.html", manga=manga, cover=cover, chapters=chapters)


@app.route("/chapter/<chapter_id>")
def read_chapter(chapter_id):
    images = api.get_chapter_images(chapter_id)
    if not images:
        return "Chapter not available", 404

    return render_template("reader.html", images=images, chapter_id=chapter_id)


@app.route("/download/<chapter_id>")
def download_chapter(chapter_id):
    success = api.download_chapter(chapter_id)
    if success:
        return f"Chapter {chapter_id} downloaded successfully!"
    return "Failed to download chapter.", 500


if __name__ == "__main__":
    app.run(debug=True, port="8086", host="0.0.0.0")
