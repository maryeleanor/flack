import os 
import functools
from flask import Flask, render_template, url_for, jsonify, request, session, redirect, flash
from flask_socketio import SocketIO, emit, disconnect, join_room
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") 
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app, manage_session=False)
 
login_manager = LoginManager()
login_manager.init_app(app)  

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/", methods=["GET", "POST"])
def index():
    #if user clicked login
    if request.method == "POST":

        #get username from form
        username = request.form.get("username")
        
        # ensure username was submitted
        if not username: 
            flash(u'Invalid credentials', 'error')
            return render_template("register.html")
 
        # remember which user has logged in
        session["username"] = username
        
        # redirect user to home page
        flash('You were successfully logged in.')
        return render_template("index.html")

    # user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@socketio.on("submit chat")
def chat(data):
    chat = data["message"]
    username = session["username"]
    print(f'{username}: {chat}') 
    emit("chat added", {"chat": chat, "username": username}, broadcast=True)
  
@app.route("/account") 
def account():
     
    # Redirect user to account page
    return render_template("account.html")


@app.route("/logout") 
def logout():
    # Forget username
    session.clear()

    # Redirect user to homepage
    return redirect("/")

 
