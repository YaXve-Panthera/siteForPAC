from flask import Flask, template_rendered, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dataBase import DataBase
from user import User

app = Flask(__name__)
app.config.from_object(__name__)
dBase = None
login_manager = LoginManager(app)
login_manager.login_view = '/login'


@app.before_request
def before_request():
    print("db is work")
    global dBase
    dBase = DataBase("siteBase")


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return User().fromDB(user_id)


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        if request.form['password'] == request.form['repeatpassword']:
            if dBase.checkUser(request.form['email']):
                hash = generate_password_hash(request.form['password'])
                res = dBase.addUser({'email' : request.form['email'], 'password': hash, 'name': request.form['name']})
                return "u success registered"
            else:
                return "user with this email already registered"
        else:
            return "passwords not equal"
    return render_template("registration.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        print("try to login " + str(request.form['email']))
        user = dBase.getUserByEmail(request.form['email'])
        print("get user from bd" + str(user))
        if user is not None:
            if check_password_hash(user['password'], request.form['password']):
                print("password is correct")
                userlogin = User().create(user)
                print("created class user")
                login_user(userlogin)
                return redirect("profile")
            else:
                return "password incorrect"
        else:
            return "user not found"
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<a href="{url_for('logout')}">Выйти из профиля</a>
                    user info: {current_user.get_id()}"""




if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)
