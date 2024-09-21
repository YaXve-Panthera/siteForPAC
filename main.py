from flask import Flask, template_rendered, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from dataBase import DataBase
from user import User

app = Flask(__name__)

dBase = DataBase("siteBase")


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        if request.form['password'] == request.form['repeatpassword']:
            if dBase.checkUser(request.form['email']):
                hash = generate_password_hash(request.form['password'])
                res = dBase.addUser(User(request.form['email'], hash, request.form['name']))
            else:
                return "user with this email alredy registered"
        else:
            return "passwords not equal"
    return render_template("registration.html")


@app.route('/login')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
