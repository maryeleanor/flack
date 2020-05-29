import os 
import functools
import random
import datetime
import time 
from collections import deque
from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room, send
from flask_session import Session
from werkzeug.utils import secure_filename

# set configs and env variables
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["SESSION_TYPE"] = "filesystem" 
app.config["ALLOWED_IMAGE_EXENSIONS"] = ["PNG", "JPG", "JPEG", "GIF", "SVG"] 
app.config["MAX_IMG_SIZE"] = 2 * 1024 * 1024 

Session(app)
socketio = SocketIO(app, manage_session=False) 

# declare dict for messages and array for rooms 
messages = {'Home': deque(maxlen=100), 'News': deque(maxlen=100), 'Another Room': deque(maxlen=100)}
rooms = ["Home", "News", "Another Room"]

@app.route("/", methods=["GET", "POST"])
def index():
    
    # if user accessed via form
    if request.method == "POST":
        
        # if user clicked create new channel
        if request.form.get("channel"):
            new_channel = True;
            room = request.form.get("channel")
            room = room.capitalize()
            if room == 'None' or room == 'Create new channel':
                room = 'Home'
            username = None
            if 'username' in session:
                username = session["username"]

            # check if channel exists
            if room in rooms:
                error = 'That room already exists.'
                session["room"] = room 
                return render_template("index.html", username=username, room=room, rooms=rooms, error=error, new_channel=new_channel)

            # if not, add to rooms array and messages dict    
            else:
                rooms.append(room)
                messages.update({room: deque(maxlen=100)})
                session["room"] = room
                return render_template("index.html", username=username, room=room, rooms=rooms, new_channel=new_channel)

        #get username and room from form
        username = request.form.get("username")
        room = request.form.get("room")
        
        # remember user and room choice
        session["username"] = username
        session["room"] = room
        
        #assign a profile pic
        if 'image_file' in session:
            image_file = session["image_file"] 
        else:
            number = random.randint(1,12)
            userimg = 'user' + str(number) + '.png'
            image_file = url_for('static', filename="imgs/" + userimg) 
            session["image_file"] = image_file
    
        # redirect back to home page   
        return render_template("index.html", username=username, room=room, rooms=rooms, image_file=image_file)
 
    # user reached route via GET, has not yet submitted any of the forms
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

# on socket 'Connect to room '
@socketio.on('connect to room')
def connection(data):
    # get username and image from session
    username = None
    if 'username' in session:
        username = session["username"]
    image_file = None
    if 'image_file' in session:
        image_file = session["image_file"] 
    # get room from json data, or session if no room passed in
    room = data["room"]
    if 'room' in session:
        room = session["room"]

    join_room(room)    
    timestamp = time.time()
    sysmsg = data["msg"]
        
    # if new room, add to rooms array and messages dict     
    if room not in rooms:
        session["room"] = room
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})

    # pass in current room messages as list   
    current_room_messages = list(messages[room])
    send({'sysmsg': sysmsg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)

# when 'Send chat' button is clicked
@socketio.on('send chat')
def chat(data):
    username = session["username"]
    image_file = session["image_file"] 
    chat = data["chat"]
    room = data["room"]
    session['room'] = room
    timestamp = time.time()
    room_messages = messages[room]
    row = {'username': username, 'image_file': image_file, 'timestamp': timestamp, 'chat': chat, 'room':room}
    room_messages.append(row)
    messages[room] = room_messages
    send({'chat': chat, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room}, room=room)
  

# if room button clicked
@socketio.on('join')
def join(data):
    username = session['username']
    image_file = session["image_file"] 
    timestamp = time.time()
    sysmsg = " has entered "
    room = data['room']
    session['room'] = room
    join_room(room)
    
    # if new room, add to rooms array and messages dict     
    if room not in rooms:
        session["room"] = room
        rooms.append(room)
        messages.update({room: deque(maxlen=100)})

    # pass in current room messages as list   
    current_room_messages = list(messages[room])
    send({'sysmsg': sysmsg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room, 'messages': current_room_messages}, room=room)


# if user clicks to another room, run leave on old room
@socketio.on('leave')
def leave(data):
    username = data['username']
    image_file = session["image_file"] 
    room = data['room']
    timestamp = time.time()
    sysmsg = " has left "
    leave_room(room)
    send({'sysmsg': sysmsg, 'username': username, 'image_file': image_file, 'timestamp': timestamp, 'room': room}, room=room)

# function to check for allowed image files
def allowed_img(filename):
    if not "." in filename:
        return None
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXENSIONS"]:
        return ext
    else:
        return None
 
# profile / account page route
@app.route("/account",  methods=["GET", "POST"]) 
def account():
    #get current username and image
    if 'username' in session:
        username = session["username"]
    image_file = session["image_file"]  

    # if user submits profile update via POST
    if request.method == "POST": 
        #if user submited an image file
        if request.files:
            image = request.files['image']
            if image:
                # check filesize
                if (int(request.cookies['filesize']) > app.config["MAX_IMG_SIZE"]): 
                    error = "Image file is too large"
                    return render_template("account.html", username=username, error=error, image_file=image_file)

                # check filetype / extension
                ext = allowed_img(image.filename)
                if not ext:
                    error = "Filetype not allowed"
                    return render_template("account.html", username=username, error=error, image_file=image_file)

                # save with new filename
                filename = secure_filename(session['username'] + "-" + image.filename)
                image.save(os.path.join(app.root_path, 'static/imgs/', filename))

                #save new image and success message
                success = "successfully uploaded"
                image_file = url_for('static', filename="imgs/" + filename)
                session["image_file"] = image_file 

            # if users entered an updated username, save in session
            new_username = request.form.get("username")
            if new_username:
                username = new_username
                session["username"] = username
       
            success = "successfully updated"

            # return profile page with success
            return render_template("account.html", username=username, success=success, image_file=image_file)

    # return account page
    return render_template("account.html", username=username, image_file=image_file)

# logout route: removes everything from session, which in this app means all user info is lost from that user
@app.route("/logout") 
def logout():
    session.pop('username', None)
    session.pop('room', None)  
    session.pop('image_file', None)
    # Redirect user to homepage
    return redirect("/")

 
