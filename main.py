from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dataBase import DataBase
from forms import LoginForm, RegistrationForm, CreateChatForm
from user import User

app = Flask(__name__)
app.config.from_object(__name__)
dBase = DataBase("siteBase")
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
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data == form.repeatPassword.data:
            if dBase.checkUser(form.email.data):
                hash = generate_password_hash(form.password.data)
                res = dBase.addUser({'email': form.email.data, 'password': hash, 'name': form.name.data})
                return redirect(url_for("profile"))
            else:
                return "user with this email already registered"
        else:
            return "passwords not equal"
    return render_template("registration.html", form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        print("try to login " + str(form.email.data))
        user = dBase.getUserByEmail(form.email.data)
        print("get user from bd" + str(user))
        if user is not None:
            if check_password_hash(user['password'], form.password.data):
                print("password is correct")
                userlogin = User().create(user)
                print("created class user")
                login_user(userlogin)
                return redirect("profile")
            else:
                return "password incorrect"
        else:
            return "user not found"
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


@app.route('/profilesettings',  methods=["POST", "GET"])
@login_required
def profilesettings():
    id = current_user.get_id()
    if request.method == "POST":
        if request.args.get("f") == "prof":
            print("updated profile")
            print(id)
            print(current_user)
            res = dBase.updateUser(id, request.form['name'], request.form['age'],
                                   request.form['aboutUser'])
            return redirect(url_for("profile"))

        if request.args.get("f") == "pass":
            if check_password_hash(dBase.getHash(id), request.form['oldpassword']):
                if request.form['newpassword'] == request.form['repeatpassword']:
                    print("changing password")
                    print(id)
                    res = dBase.updatePassword(id, generate_password_hash(request.form['newpassword']))
                    return redirect(url_for("profile"))
                else:
                    return "passwords no equal"
            else:
                return "wrong password"
    return render_template("profilesettings.html")

@app.route('/chatlist', methods=["POST", "GET"])
@login_required
def chatlist():
    form = CreateChatForm()
    form.chooses.choices = dBase.listOfUsers()
    if form.validate_on_submit():
        print("creating new chat")
        if form.name.data == "" or form.name.data is None:
            nm = dBase.getNameById(form.chooses.data)
        else:
            nm = form.name.data
        users = [current_user.get_id(), form.chooses.data]
        dBase.addChat(nm, users)

    chats = dBase.listOfUserChat(current_user.get_id())

    print(chats)
    return render_template("chatlist.html", form=form, chats=chats)

@app.route('/chat/<chatid>', methods=["POST", "GET"])
@login_required
def chat(chatid):
    print(chatid)
    chat = dBase.getChatById(chatid)
    return render_template("chat.html", chat=chat)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)
