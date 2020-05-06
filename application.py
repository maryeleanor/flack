import os 

from flask import Flask, render_template, url_for, jsonify
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chats = []

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("submit chat")
def chat(data):
    chat = data["message"]
    print(chat)
    emit("chat added", {"chat": chat}, broadcast=True)


@socketio.on("submit vote")
def vote(data):
    selection = data["selection"]
    emit("announce vote", {"selection": selection}, broadcast=True)
