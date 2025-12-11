# the main entry of the program/site
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/","/home")
def home_page():
    return render_template("home.html")

@app.route('/signup')

if __name__ == "__main__":
    app.run(debug=True)
