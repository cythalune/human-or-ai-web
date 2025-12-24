from google import genai
import random
import json
import sqlite3
import os
import time

with open('qa.json', 'r', encoding='utf-8') as f:
    QA_DATA = json.load(f)

ROUNDS = 5

client = genai.Client(api_key="Your-API-Key-Here")

def pick_question(used_indices):
    total = len(QA_DATA)
    available = [i for i in range(total) if i not in used_indices]
    if not available:
        available = list(range(total))
    idx = random.choice(available)
    return idx, QA_DATA[idx]

def generate_ai_answer(question):
    prompt = f"{question} be casual, concise not over-explain not mention 'AI,' 'model,' or 'assistant'"
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=(prompt,),
    )
    return response.text if hasattr(response, 'text') else str(response)

def get_answer_text(item, mode):
    if mode == 'A':
        return generate_ai_answer(item.get('question', ''))
    time.sleep(random.randint(1,2))
    return item.get('human_answer', '')

def save_score(name, score, total_time, db_path='test.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER,
            time_taken REAL
        )
        '''
    )
    cur.execute('INSERT INTO scores (name, score, time_taken) VALUES (?, ?, ?)', (name, score, total_time))
    conn.commit()
    conn.close()