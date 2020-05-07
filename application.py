import os 
import functools
from collections import deque
from flask import Flask, render_template, url_for, jsonify, request, session, redirect, flash
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room, close_room, rooms 
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app, manage_session=False) 

home = deque(maxlen=100)

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
        flash('You were successfully logged in.')
        home_room = list(home)
        return render_template("index.html", username = username, home_room = home_room)
 
    # user reached route via GET (as by clicking a link or via redirect)
    else:
        username = None
        if 'username' in session:
            username = session["username"]
        
        home_room = list(home) 
        return render_template("index.html", username = username, home_room = home_room)


@socketio.on("submit chat")
def chat(data):
    chat = data["message"]
    username = session["username"]
    message = username + ": " + chat 

    home.append(message) 
    home_room = list(home) 

    emit("chat added", {"chat": message, "home": home_room}, broadcast=True)
  
@socketio.on('join')
def on_join(data):
    username = session['username']
    room = data['room']
    join_room(room2)
    send(username + ' has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)



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

 
