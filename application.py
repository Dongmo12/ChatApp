from flask import render_template, redirect, url_for, flash
from app import wtform_fields, db, app
from app.models import User
from passlib.hash import  pbkdf2_sha512
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, send, emit,  join_room, leave_room
from time import localtime, strftime


# configurer le flask-login

login = LoginManager(app)
login.init_app(app)

# flask-socketio

socketio = SocketIO(app, manage_session=False)
ROOMS = ["classmates", "friends", "acquaintances", "family"]


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = wtform_fields.RegistrationForm()
    if reg_form.validate_on_submit():

        username = reg_form.username.data
        password = reg_form.password.data
        hash_pass = pbkdf2_sha512.hash(password)
        user = User(username=username, password=hash_pass)
        db.session.add(user)
        db.session.commit()

        flash("Registered ! Log in now.", "win")
        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = wtform_fields.LoginForm()
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username = login_form.username.data).first()
        login_user(user_object)

        return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        flash("Log in before!", "fail")
        return redirect(url_for('login'))
    return render_template('chat.html', username=current_user.username, rooms=ROOMS)




@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    flash("Logged out!", "win")
    return redirect(url_for('login'))


# create events handler


@socketio.on('message')
def message(data):
#    room = data["room"]
    #print(f"\n\n{data}\n\n")
    send({'msg': data['msg'], 'username': data['username'],
    'time_stamp': strftime('%b-%d %I:%M%p', localtime())} #, room=room)
         )


@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + " just joined the " + data['room'] + " room."}, room=data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " just left the " + data['room'] + " room."}, room=data['room'])

