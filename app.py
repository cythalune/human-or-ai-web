from flask import Flask, render_template, request, redirect, session
from google import genai
from helpers import *
import random
import time
import sqlite3
import json
import os

#Type your API key here
client = genai.Client(api_key="Your-API-Key-Here")

app = Flask(__name__)
app.secret_key = "dev"  # change later if you want

# Load questions
with open("qa.json", "r", encoding="utf-8") as f:
    QA_DATA = json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        session["name"] = request.form["name"]
        session["round"] = 1
        session["score"] = 0
        session["start_time"] = time.time()
        session["used"] = []

        return redirect("/game")

    return render_template("start.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    if "name" not in session:
        return redirect("/")

    rounds = ROUNDS

    if request.method == "POST":
        guess = request.form.get("guess", "").strip().upper()
        current = session.get("current")
        if not current:
            return redirect("/game")
        mode = current.get("mode")
        if guess in ("H", "A"):
            if guess == mode:
                session["score"] = session.get("score", 0) + 1
                session["last_result"] = "Correct"
            else:
                session["last_result"] = "Incorrect"
        session["round"] = session.get("round", 1) + 1
        session.pop("current", None)

        if session["round"] > rounds:
            total_time = round(time.time() - session["start_time"], 2)
            save_score(session["name"], session["score"], total_time)
            return redirect("/result")

        return redirect("/game")

    # GET
    if session.get("round", 1) > rounds:
        return redirect("/result")

    used = session.get("used", [])
    idx, item = pick_question(used)
    mode = random.choice(["H", "A"])
    answer = get_answer_text(item, mode)

    used.append(idx)
    session["used"] = used
    session["current"] = {"index": idx, "mode": mode, "question": item.get("question"), "answer": answer}

    return render_template(
        "game.html",
        question=item.get("question"),
        answer=answer,
        round=session.get("round", 1),
        rounds=rounds,
        score=session.get("score", 0),
        last_result=session.get("last_result")
    )



@app.route("/result")
def result():
    total_time = round(time.time() - session["start_time"], 2)

    return render_template(
        "result.html",
        name=session["name"],
        score=session["score"],
        time=total_time
    )

@app.route("/scoreboard")
def scoreboard():
    db_path = "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT name, score, time_taken FROM scores ORDER BY score DESC, time_taken ASC LIMIT 10"
        )
        scores = cur.fetchall()

    return render_template("scoreboard.html", scores=scores)
    

if __name__ == "__main__":
    app.run(debug=True)
