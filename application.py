import os 
import functools
from time import localtime, strftime
from collections import deque
from flask import Flask, render_template, url_for, jsonify, request, session, redirect, flash
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room, close_room, rooms, send
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app, manage_session=False) 

home = deque(maxlen=100)
rooms = ["home", "news", "another room"]

@app.route("/", methods=["GET", "POST"])
def index():
    #if user clicked login
    if request.method == "POST":

        #get username from form
        username = request.form.get("username")
        
        # ensure username was submitted
        if not username: 
            flash(u'Invalid credentials', 'error')
            return render_template("index.html")
 
        # remember which user has logged in
        session["username"] = username
        
        # redirect user back to home page
        # flash('You were successfully logged in.')
        home_room = list(home)
        room = 'home'
        return render_template("index.html", username = username, rooms=rooms, room=room)
 
    # user reached route via GET (as by clicking a link or via redirect)
    else:
        username = None
        if 'username' in session:
            username = session["username"]
        room = 'home'
        # home_room = list(home) 
        return render_template("index.html", username = username, room = room, rooms=rooms)


@socketio.on('connect to room')
def connection(data):
    username = session["username"]
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    msg = data["msg"]
    room = 'home'
    # msg = time_stamp + username + msg
    print(msg)
    send({'msg': msg, 'username': username, 'timestamp': timestamp, 'room': room}, room=room, broadcast=True)


@socketio.on('send chat')
def chat(data):
    username = session["username"]
    chat = data["chat"]
    room = data["room"]
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    # message = username + ": " + chat 
    # msg = data['message']
    # home.append(message) 
    # home_room = list(home) 
    send({'chat': chat, 'username': username, 'timestamp': timestamp, 'room': room}, room=room)
  

@socketio.on('join')
def join(data):
    username = session['username']
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    chat = " has entered "
    join_room(room)
    # send({'msg': msg, 'username': username, 'timestamp': timestamp, "room":room}, room=room)
    send({'sysmsg': chat, 'username': username, 'timestamp': timestamp, 'room': room}, room=room)


@socketio.on('leave')
def leave(data):
    username = data['username']
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    chat = " has left "
    leave_room(room)
    #send({'msg': msg, 'username': username, 'timestamp': timestamp, "room":room}, room=room)
    send({'sysmsg': chat, 'username': username, 'timestamp': timestamp, 'room': room}, room=room)



@app.route("/account") 
def account():
    if 'username' in session:
        username = session["username"]

    # Redirect user to account page
    return render_template("account.html", username=username)


@app.route("/logout") 
def logout():
    session.pop('username', None)

    # Redirect user to homepage
    return redirect("/")

 
