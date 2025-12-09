from flask import Flask

app = Flask(__name__)


@app.route("/")
def hero_section():
    pass


if __name__ == "__main__":
    app.run(debug=True)
