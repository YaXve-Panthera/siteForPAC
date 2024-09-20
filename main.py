from flask import Flask, template_rendered, render_template, request
import pymongo

app = Flask(__name__)


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
user_db = myclient["authentication"]
user_table = user_db["user_info"]

@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")


@app.route('/registration')
def registration():
    return render_template("registration.html")


@app.route('/login')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
