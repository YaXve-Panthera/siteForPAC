from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from werkzeug.security import generate_password_hash, check_password_hash
from dataBase import DataBase
from forms import LoginForm, RegistrationForm, CreateChatForm, SendMessage, UpdateProfile, ChangePassword, \
    CreateGroupChatForm
from user import User
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)
dBase = DataBase("siteBase")
login_manager = LoginManager(app)
login_manager.login_view = '/login'
socketio = SocketIO(app)


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


@app.route('/profilesettings', methods=["POST", "GET"])
@login_required
def profilesettings():
    id = current_user.get_id()

    formUP = UpdateProfile()
    formCP = ChangePassword()

    if formUP.validate_on_submit():
        print("updated profile")
        print(id)
        print(current_user)
        res = dBase.updateUser(id, formUP.name.data, formUP.age.data,
                                formUP.aboutUser.data)
        return redirect(url_for("profile"))

    if formCP.validate_on_submit():
        if check_password_hash(dBase.getHash(id), formCP.oldpassword.data):
            if formCP.newpassword.data == formCP.repeatpassword.data:
                print("changing password")
                print(id)
                res = dBase.updatePassword(id, generate_password_hash(formCP.newpassword.data))
                return redirect(url_for("profile"))
            else:
                return "passwords no equal"
        else:
            return "wrong password"
    return render_template("profilesettings.html", formCP=formCP, formUP=formUP)


@app.route('/chatlist', methods=["POST", "GET"])
@login_required
def chatlist():
    form = CreateChatForm()
    form.chooses.choices = dBase.listOfUsers()
    formG = CreateGroupChatForm()
    formG.chooses.choices = dBase.listOfUsers()
    if form.validate_on_submit():
        print("creating new chat")
        if form.name.data == "" or form.name.data is None:
            nm = dBase.getNameById(form.chooses.data)
        else:
            nm = form.name.data
        users = [current_user.get_id(), form.chooses.data]
        dBase.addChat(nm, users)

    if formG.validate_on_submit():
        print("creating new group chat")
        print(formG.data)
        if formG.name.data == "" or formG.name.data is None:
            for n in formG.chooses.data:
                nm = nm + dBase.getNameById(n) + " "

        else:
            nm = formG.name.data
        users = [current_user.get_id(), formG.chooses.data]
        dBase.addChat(nm, users)

    chats = dBase.listOfUserChat(current_user.get_id())

    print(chats)
    return render_template("chatlist.html", form=form, formG=formG, chats=chats)


@app.route('/chat/<chatid>', methods=["POST", "GET"])
@login_required
def chat(chatid):
    print("we in chat " + chatid)
    chat = dBase.getChatById(chatid)
    if current_user.get_id() not in chat['users']:
        return "Ты куда тебе нельзя"
    messages = sorted(dBase.listOfMessages(chatid), key=lambda d: d['time'])
    print(messages)
    """
    form = SendMessage()
    if form.validate_on_submit():
        print("sending message" + form.text.data)
        res = dBase.addMessage(form.text.data, chatid, current_user.get_id(), datetime.now())
        return render_template("chat.html", chat=chat, messages=sorted(dBase.listOfMessages(chatid),
                                                                       key=lambda d: d['time']), form=form, db=dBase)
    """
    return render_template("chat.html", chat=chat, messages=messages, db=dBase)


# WebSocket events
@socketio.on('join')
@login_required
def on_join(data):
    room = data['room']
    join_room(room)
    #emit('message', {'msg': f'{current_user.get_name()} has entered the room.'}, room=room)


@socketio.on('leave')
@login_required
def on_leave(data):
    room = data['room']
    leave_room(room)
    #emit('message', {'msg': f'{current_user.get_name()} has left the room.'}, room=room)


@socketio.on('send_message')
@login_required
def handle_send_message(data):
    room = data['room']
    message = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("handle message" + str(room))
    # Save message to the database
    dBase.addMessage(message, room, current_user.get_id(), datetime.now())

    # Broadcast the message to the room
    emit('message', {'msg': f'{current_user.get_name()}: {message}', 'timestamp': timestamp}, room=room)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    socketio.run(app=app, debug=True, allow_unsafe_werkzeug=True, port=3000, host='0.0.0.0')
