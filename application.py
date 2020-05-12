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
 
messages = {'Home': deque(maxlen=100), 'News': deque(maxlen=100), 'Another Room': deque(maxlen=100)}
rooms = ["Home", "News", "Another Room"]

@app.route("/", methods=["GET", "POST"])
def index():
    # if user submitted via form
    if request.method == "POST":

        # if user clicked create new channel
        if request.form.get("channel"):
            room = request.form.get("channel")
            room = room.capitalize()
            username = None
            if 'username' in session:
                username = session["username"]

            # check if channel exists
            if room in rooms:
                error = 'That room already exists.'
                session["room"] = room 
                return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages, error=error)
            else:
                rooms.append(room)
                messages.update({room: deque(maxlen=100)})
                session["room"] = room
                return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages)

        #get username and room from form
        username = request.form.get("username")
        room = request.form.get("room")
        print(room)
         
        # remember user room choice
        session["username"] = username
        session["room"] = room
        
        # redirect back to home page   
        return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages)
 
    # user reached route via GET 
    else:
        username = None
        if 'username' in session:
            username = session["username"]
        room = None 
        if 'room' in session:
            room = session["room"] 
        print(room)
        return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages)


@socketio.on('connect to room')
def connection(data):
    username = session["username"]
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    msg = data["msg"]
    room = session["room"]
    join_room(room)

    if room in rooms:
        room_messages = messages[room]
        row = {'username': username, 'timestamp': timestamp, 'msg': msg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
        print(messages[room])
    else:
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})
        room_messages = messages[room]
        row = {'username': username, 'timestamp': timestamp, 'msg': msg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
        print(messages[room])

    current_room_messages = list(messages[room])
    send({'msg': msg, 'username': username, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)


@socketio.on('send chat')
def chat(data):
    username = session["username"]
    chat = data["chat"]
    room = data["room"]
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    room_messages = messages[room]
    row = {'username': username, 'timestamp': timestamp, 'chat': chat, 'room':room}
    room_messages.append(row)
    messages[room] = room_messages
    send({'chat': chat, 'username': username, 'timestamp': timestamp, 'room': room}, room=room)
  

@socketio.on('join')
def join(data):
    username = session['username']
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    sysmsg = " has entered "
    join_room(room)
    if room in rooms:
        room_messages = messages[room]
        row = {'username': username, 'timestamp': timestamp, 'sysmsg': sysmsg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
    else:
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})
        room_messages = messages[room]
        row = {'username': username, 'timestamp': timestamp, 'sysmsg': sysmsg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
    current_room_messages = list(messages[room])
    print(current_room_messages)
    send({'sysmsg': sysmsg, 'username': username, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)


@socketio.on('leave')
def leave(data):
    username = data['username']
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    sysmsg = " has left "
    leave_room(room)
    send({'sysmsg': sysmsg, 'username': username, 'timestamp': timestamp, 'room': room}, room=room)



@app.route("/account") 
def account():
    if 'username' in session:
        username = session["username"]

    # Redirect user to account page
    return render_template("account.html", username=username)


@app.route("/logout") 
def logout():
    session.pop('username', None)
    session.pop('room', None)  
    # Redirect user to homepage
    return redirect("/")

 
