import os 
import functools
import random
from time import localtime, strftime
from collections import deque
from flask import Flask, render_template, url_for, jsonify, request, session, redirect, flash
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room, close_room, rooms, send
from flask_session import Session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["SESSION_TYPE"] = "filesystem" 
app.config["ALLOWED_IMAGE_EXENSIONS"] = ["PNG", "JPG", "JPEG", "GIF", "SVG"] 
app.config["MAX_IMG_SIZE"] = 2 * 1024 * 1024 

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
         
        # remember user and room choice
        session["username"] = username
        session["room"] = room
        
        #assign a profile pic
        number = random.randint(1,12)
        userimg = 'user' + str(number) + '.png'
        image_file = url_for('static', filename="imgs/" + userimg) 
        session["image_file"] = image_file
    
        # redirect back to home page   
        return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages, image_file=image_file)
 
    # user reached route via GET 
    username = None
    if 'username' in session:
        username = session["username"]
    room = None 
    if 'room' in session:
        room = session["room"] 
    
    if 'image_file' in session:
        image_file = session["image_file"] 
    else:
        number = random.randint(1,12)
        userimg = 'user' + str(number) + '.png'
        image_file = url_for('static', filename="imgs/" + userimg) 

    return render_template("index.html", username=username, room=room, rooms=rooms, messages=messages, image_file=image_file)


@socketio.on('connect to room')
def connection(data):
    username = None
    if 'username' in session:
        username = session["username"]
    image_file = None
    if 'image_file' in session:
        image_file = session["image_file"] 
    
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    msg = data["msg"]
    room = data["room"]
    join_room(room)

    if room in rooms:
        room_messages = messages[room]
        row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'msg': msg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
         
    else:
        session["room"] = room
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})
        room_messages = messages[room]
        row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'msg': msg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
        
    current_room_messages = list(messages[room])
    send({'msg': msg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)


@socketio.on('send chat')
def chat(data):
    username = session["username"]
    image_file = session["image_file"] 
    chat = data["chat"]
    room = data["room"]
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    room_messages = messages[room]
    row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'chat': chat, 'room':room}
    room_messages.append(row)
    messages[room] = room_messages
    send({'chat': chat, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room}, room=room)
  

@socketio.on('join')
def join(data):
    username = session['username']
    image_file = session["image_file"] 
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    sysmsg = " has entered "
    join_room(room)
    if room in rooms:
        room_messages = messages[room]
        row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'sysmsg': sysmsg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
    else:
        session["room"] = room
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})
        room_messages = messages[room]
        row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'sysmsg': sysmsg, 'room':room}
        room_messages.append(row)
        messages[room] = room_messages
    current_room_messages = list(messages[room])
     
    send({'sysmsg': sysmsg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)


@socketio.on('leave')
def leave(data):
    username = data['username']
    image_file = session["image_file"] 
    room = data['room']
    timestamp = strftime('%b %d, %I:%M %p', localtime())
    sysmsg = " has left "
    leave_room(room)
    send({'sysmsg': sysmsg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room}, room=room)


def allowed_img(filename):
    if not "." in filename:
        return None
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXENSIONS"]:
        return ext
    else:
        return None
 

@app.route("/account",  methods=["GET", "POST"]) 
def account():
    if 'username' in session:
        username = session["username"]

    image_file = session["image_file"]  

    # if user submits profile update via POST
    if request.method == "POST": 
        if request.files:
            image = request.files['image']
            if image:
                if (int(request.cookies['filesize']) > app.config["MAX_IMG_SIZE"]): 
                    error = "Image file is too large"
                    return render_template("account.html", username=username, error=error)

                ext = allowed_img(image.filename)
                if not ext:
                    error = "Filetype not allowed"
                    return render_template("account.html", username=username, error=error)

                filename = secure_filename(session['username'] + image.filename)
                image.save(os.path.join(app.root_path, 'static/imgs/', filename))
                success = "successfully uploaded"
                image_file = url_for('static', filename="imgs/" + filename)
                session["image_file"] = image_file
                return render_template("account.html", username=username, success=success, image_file=image_file)
            
            username = request.form.get("username")
            session["username"] = username
            return render_template("account.html", username=username, image_file=image_file)

    # route account page
    return render_template("account.html", username=username, image_file=image_file)


@app.route("/logout") 
def logout():
    session.pop('username', None)
    session.pop('room', None)  
    session.pop('image_file', None)
    # Redirect user to homepage
    return redirect("/")

 
