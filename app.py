from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import uuid
import os
from flask import Response
import time

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

clients = []
DATA_FILE = "messages.json"
USERS = ["user1", "user2"]

def load_messages():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_messages(msgs):
    with open(DATA_FILE, "w") as f:
        json.dump(msgs, f, indent=2)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/<user>")
def chat(user):
    if user not in USERS:
        return "User not found", 404
    return render_template("chat.html", user=user)

@app.route("/api/messages", methods=["GET"])
def get_messages():
    return jsonify(load_messages())

@app.route("/api/send", methods=["POST"])
def send_message():
    data = request.json
    with open("messages.json") as f:
        messages = json.load(f)
    messages.append({
        "id": str(uuid.uuid4()),
        "user": data["user"],
        "text": data["text"],
        "time": datetime.now().strftime("%H:%M"),
        "deleted": False
    })
    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=2)
    return "", 204


@app.route("/api/delete/<msg_id>", methods=["POST"])
def delete(msg_id):
    msgs = load_messages()
    msgs = [m for m in msgs if m["id"] != msg_id]
    save_messages(msgs)
    return jsonify({"status": "ok"})

@app.route("/api/edit/<msg_id>", methods=["POST"])
def edit(msg_id):
    data = request.json
    msgs = load_messages()
    for m in msgs:
        if m["id"] == msg_id:
            m["text"] = data["text"]
            m["edited"] = True
    save_messages(msgs)
    return jsonify({"status": "ok"})

@app.route('/stream')
def stream():
    def event_stream():
        last = ""
        while True:
            with open("messages.json") as f:
                data = f.read()
            if data != last:
                last = data
                yield f"data: {data}\n\n"
            time.sleep(0.5)
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/events")
def events():
    def stream():
        last = ""
        while True:
            time.sleep(0.5)
            with open("messages.json") as f:
                data = json.load(f)
            new = json.dumps(data)
            if new != last:
                yield f"data: {new}\n\n"
                last = new
    return Response(stream(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

