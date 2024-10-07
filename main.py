from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, emit
from werkzeug.security import generate_password_hash, check_password_hash
from dataBase import DataBase
from forms import LoginForm, RegistrationForm, CreateChatForm, UpdateProfile, ChangePassword, \
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
    print("[main] init database")
    global dBase
    dBase = DataBase("siteBase")


@app.route('/')
@app.route('/home')
def index():
    print("[main] page: home")
    return render_template("home.html")


@login_manager.user_loader
def load_user(user_id):
    print(f'[main] user_loader:{user_id}')
    return User().from_db(user_id)


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if current_user.is_authenticated:
        print("[main] redirecting: profile")
        return redirect(url_for('profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data == form.repeatPassword.data:
            if dBase.check_user(form.email.data):
                hash_password = generate_password_hash(form.password.data)
                res = dBase.add_user({'email': form.email.data, 'password': hash_password, 'name': form.name.data})
                print(f'[main] [registration] email:{form.email.data}, name:{form.name.data}')
                return redirect(url_for("profile"))
            else:
                print(f'[main] [registration] error: user with this email already registered | email:{form.email.data}')
                return "user with this email already registered"
        else:
            print(f'[main] [registration] error: passwords not equal | email:{form.email.data}')
            return "passwords not equal"
    print("[main] page: registration")
    return render_template("registration.html", form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        print("[main] redirecting: profile")
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        # print("try to login " + str(form.email.data))
        user = dBase.get_user_by_email(form.email.data)
        # print("get user from bd" + str(user))
        if user is not None:
            if check_password_hash(user['password'], form.password.data):
                # print("password is correct")
                userlogin = User().create(user)
                # print("created class user")
                login_user(userlogin)
                print(f'[main] [login] success! email:{form.email.data}')
                print("[main] redirecting: profile")
                return redirect("profile")
            else:
                print(f'[main] [login] error: password incorrect | email:{form.email.data}')
                return "password incorrect"
        else:
            print(f'[main] [login] error: user not found | email:{form.email.data}')
            return "user not found"
    print("[main] page: login")
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    print(f'[main] logout email:{current_user.get_email()}')
    logout_user()
    print("[main] redirecting: login")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    print(f'[main] page: profile email:{current_user.get_email()}')
    return render_template("profile.html")


@app.route('/profilesettings', methods=["POST", "GET"])
@login_required
def profilesettings():
    current_id = current_user.get_id()

    form_up = UpdateProfile()
    form_cp = ChangePassword()

    if form_up.validate_on_submit():
        # print("updated profile")
        # print(id)
        # print(current_user)
        res = dBase.update_user(current_id, form_up.name.data, form_up.age.data, form_up.aboutUser.data)
        print(
            f'[main] profile update email:{current_user.get_email()}, new name: {form_up.name.data},\
             new age {form_up.age.data}, new About: {form_up.aboutUser.data}')
        return redirect(url_for("profile"))

    if form_cp.validate_on_submit():
        if check_password_hash(dBase.get_hash(current_id), form_cp.oldpassword.data):
            if form_cp.newpassword.data == form_cp.repeatpassword.data:
                # print("changing password")
                # print(id)
                res = dBase.update_password(current_id, generate_password_hash(form_cp.newpassword.data))
                print(f'[main] page: passwrod update email:{current_user.get_email()}')
                print("[main] redirecting: profile")
                return redirect(url_for("profile"))
            else:
                print(f'[main] [profile settings] error: passwords no equal | email:{current_user.get_email()}')
                return "passwords no equal"
        else:
            print(f'[main] [profile settings] error: passwords no equal | email:{current_user.get_email()}')
            return "wrong password"
    print(f'[main] page: profile settings email:{current_user.get_email()}')
    return render_template("profilesettings.html", formCP=form_cp, formUP=form_up)


@app.route('/chatlist', methods=["POST", "GET"])
@login_required
def chatlist():
    nm = ""
    form = CreateChatForm()
    form.chooses.choices = dBase.get_list_of_users()
    form_g = CreateGroupChatForm()
    form_g.chooses.choices = dBase.get_list_of_users()
    if form.validate_on_submit():
        # print(f'[main] [chat] creating new chat | email:{current_user.get_email()}')
        # print("creating new chat")
        if form.name.data == "" or form.name.data is None:
            nm = dBase.get_username_by_id(form.chooses.data)
        else:
            nm = form.name.data
        users = [current_user.get_id(), form.chooses.data]
        dBase.add_chat(nm, users)
        print(f'[main] [chat] creating new chat | chat name:{nm}, users: {users}')

    if form_g.validate_on_submit():
        print("creating new group chat")
        print(form_g.data)
        if form_g.name.data == "" or form_g.name.data is None:
            for n in form_g.chooses.data:
                nm = nm + dBase.get_username_by_id(n) + " "

        else:
            nm = form_g.name.data
        users = [current_user.get_id(), form_g.chooses.data]
        dBase.add_chat(nm, users)
        print(f'[main] [chat] creating new group chat | chat name:{nm}, users: {users}')

    chats = dBase.get_user_chat_list(current_user.get_id())

    print(f'[main] page: chat list of email:{current_user.get_email()}, chats: {chats}')
    return render_template("chatlist.html", form=form, formG=form_g, chats=chats)


@app.route('/chat/<chatid>', methods=["POST", "GET"])
@login_required
def chat(chatid):
    # print("we in chat " + chatid)
    chat = dBase.get_chat_by_id(chatid)
    if current_user.get_id() not in chat['users']:
        print(f'[main] [chat] error: user not in chat {chatid}, email: {current_user.get_email()}')
        return "Ты куда тебе нельзя"
    messages = sorted(dBase.get_list_of_messages(chatid), key=lambda d: d['time'])
    print(messages)
    """
    form = SendMessage()
    if form.validate_on_submit():
        print("sending message" + form.text.data)
        res = dBase.addMessage(form.text.data, chatid, current_user.get_id(), datetime.now())
        return render_template("chat.html", chat=chat, messages=sorted(dBase.listOfMessages(chatid),
                                                                       key=lambda d: d['time']), form=form, db=dBase)
    """
    print(f'[main] page: chat {chatid} open by email:{current_user.get_email()}')
    return render_template("chat.html", chat=chat, messages=messages, db=dBase)


# WebSocket events
@socketio.on('join')
@login_required
def on_join(data):
    room = data['room']
    join_room(room)
    # emit('message', {'msg': f'{current_user.get_name()} has entered the room.'}, room=room)


@socketio.on('leave')
@login_required
def on_leave(data):
    room = data['room']
    leave_room(room)
    # emit('message', {'msg': f'{current_user.get_name()} has left the room.'}, room=room)


@socketio.on('send_message')
@login_required
def handle_send_message(data):
    room = data['room']
    message = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # print("handle message" + str(room))
    # Save message to the database
    dBase.add_message(message, room, current_user.get_id(), datetime.now())

    print(f'[main] [chat]: chat {room}, email:{current_user.get_email()}, message: {message}')
    # Broadcast the message to the room
    emit('message', {'msg': f'{current_user.get_name()}: {message}', 'timestamp': timestamp}, room=room)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    socketio.run(app=app, debug=True, allow_unsafe_werkzeug=True, port=3000, host='0.0.0.0')
    print(f'[main] start server')
