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
import os
from flask import send_file
import io
import requests

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
    """
    Home page route
    Displays welcome message depending on session or guest access
    """
    guest = request.args.get("guest")
    if guest:
        message = "You're browsing as a guest."
    elif "user" in session:
        message = f"Welcome back, {session['user']['name']}!"
    else:
        message = "Welcome to Toonix :)"

    # List of popular manga titles to feature
    featured_titles = [
        "One Piece (Official Colored)",
        "Narueto (Official Colored)",
        "Bleach",
        "JoJo's Bizarre Adventure, Part 4: Diamond Is Unbreakable (Official Colored)",
        "HUNTER x HUNTER (Official Colored)",
        "Fullmetal Alchemist",
        "Dragon Ball Super",
    ]

    featured_manga = []

    # For each popular title, search the API and take the first result
    for title in featured_titles:
        results = api.search_manga(title, limit=1)  # search top match
        if results:
            manga = results[0]  # take first item
            # get and attach cover url
            cover = api.get_manga_cover(manga)
            if cover:
                manga_id, file_name = cover
                manga["cover_url"] = url_for(
                    "cover_proxy", manga_id=manga_id, file_name=file_name
                )
            else:
                manga["cover_url"] = "/static/images/placeholder_cover.png"
            featured_manga.append(manga)

    return render_template(
        "home.html",
        message=message,
        featured_manga=featured_manga,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Signup route
    Adds a new user and redirects to login page upon success
    """
    if request.method == "POST":
        conn = db.connectDB()
        data = db.addUser(conn, request.form)
        conn.close()

        if data["status"]:
            # signup successful -> redirect to login page with message
            return redirect(url_for("intro_page"))
        else:
            # signup failed -> show signup page with error
            return render_template("signup.html", error=data["data"])

    # GET request -> show empty signup form
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route
    Authenticates user and sets session
    """
    message = None
    # Check if redirected from signup
    if request.args.get("signup") == "success":
        message = "Signup successful! Please login."

    if request.method == "POST":
        conn = db.connectDB()
        data = db.auth(conn, request.form)
        conn.close()

        if data["status"]:
            user = data["data"]
            # store name & email in session
            session["user"] = {"name": user[1], "email": user[2]}

            # login successful -> redirect to home page
            return redirect(url_for("home_page"))
        else:
            # login failed -> show login page with error
            return render_template("login.html", error=data["data"], message=message)

    # GET request -> show empty login form
    return render_template("login.html", message=message)


@app.route("/logout", methods=["POST"])
def logout():
    """
    Logout route
    Clears session and redirects to intro page
    """
    session.clear()
    return redirect(url_for("intro_page"))


@app.route("/guest")
def guest_access():
    """
    Guest access route
    Sets guest info in session and redirects to home
    """
    session["name"] = "Guest"
    session["email"] = None  # no email for guests

    return redirect(url_for("home_page", guest=1))


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Manga search route
    Returns search results from core/api.py
    """
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = api.search_manga(query)
            # Attach cover_url for each manga
            for manga in results:
                cover = api.get_manga_cover(manga)
                if cover:
                    manga_id, file_name = cover
                    manga["cover_url"] = url_for(
                        "cover_proxy", manga_id=manga_id, file_name=file_name
                    )
                else:
                    manga["cover_url"] = "/static/images/placeholder_cover.png"

    return render_template("search.html", results=results, query=query)


@app.route("/manga/<manga_id>")
def view_manga(manga_id):
    """
    Fetch metadata, cover, and chapters for a manga
    """
    manga = api.fetch_manga_local(manga_id)
    if not manga:
        return "Manga not found :(", 404

    cover = api.get_manga_cover(manga)
    if cover:
        manga_id, file_name = cover
        cover_url = url_for("cover_proxy", manga_id=manga_id, file_name=file_name)
    else:
        cover_url = "/static/images/placeholder_cover.png"

    chapters = api.get_manga_chapters(manga_id)

    return render_template(
        "manga.html", manga=manga, cover=cover_url, chapters=chapters
    )


@app.route("/chapter/<chapter_id>")
def read_chapter(chapter_id):
    """
    Reads a manga chapter
    """
    data = api.get_chapter_images(chapter_id)
    if not data:
        return "Chapter not available", 404

    images = []
    chapter_hash = data.get("hash")
    pages = data.get("pages", [])

    for page in pages:
        images.append(
            url_for(
                "page_proxy",
                chapter_hash=chapter_hash,
                file_name=page,
            )
        )

    return render_template("reader.html", images=images, chapter_id=chapter_id)


@app.route("/download/<chapter_id>")
def download_chapter(chapter_id):
    """
    Downloads a manga chapter into a structured folder:
    downloads/<manga_name>/manga-chapter-<chapter_number>
    Returns JSON status for frontend popup.
    """
    # fetch chapter data
    chapter_data = api.get_chapter_images(chapter_id)
    if not chapter_data:
        return {"status": "error", "message": "Chapter not found."}, 404

    # fetch manga info
    # find manga id from chapter metadata (Mangadex API requires it)
    chapter_info = chapter_data.get("chapter", {})
    manga_id = chapter_info.get("mangaId")
    chapter_number = chapter_info.get("chapter", "unknown")

    manga = api.fetch_manga_local(manga_id)
    if not manga:
        manga_name = "Unknown Manga"
    else:
        manga_name = manga["attributes"]["title"].get("en", "Unknown Manga")
        # sanitize folder name
        manga_name = "".join(c for c in manga_name if c.isalnum() or c in " _-").strip()

    # create download path
    chapter_dir = os.path.join(
        "downloads", manga_name, f"{manga_name}-chapter-{chapter_number}"
    )
    os.makedirs(chapter_dir, exist_ok=True)

    # download all pages
    base = chapter_data.get("base")
    pages = chapter_data.get("pages", [])
    chapter_hash = chapter_data.get("hash")

    if not base or not chapter_hash or not pages:
        return {"status": "error", "message": "Chapter data incomplete."}, 500

    for i, page in enumerate(pages):
        url = f"{api.UPLOADS_URL}/data/{chapter_hash}/{page}"
        r = requests.get(url)
        if r.status_code == 200:
            file_path = os.path.join(chapter_dir, f"page_{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(r.content)

    return {"status": "success", "message": f"Chapter {chapter_number} downloaded!"}


@app.route("/cover/<manga_id>/<file_name>")
def cover_proxy(manga_id, file_name):
    """
    Fetch cover from MangaDex and serve it locally to avoid hotlink issues
    """
    url = f"https://uploads.mangadex.org/covers/{manga_id}/{file_name}"
    r = requests.get(url)
    if r.status_code != 200:
        return "Not found", 404

    return send_file(io.BytesIO(r.content), mimetype="image/jpeg")


@app.route("/page/<chapter_hash>/<file_name>")
def page_proxy(chapter_hash, file_name):
    """
    Fetch chapter page from MangaDex and serve it locally
    to avoid hotlink protection
    """
    url = f"https://uploads.mangadex.org/data/{chapter_hash}/{file_name}"
    r = requests.get(url)
    if r.status_code != 200:
        return "Not found", 404

    return send_file(io.BytesIO(r.content), mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(debug=True, port="8084", host="0.0.0.0")
