from flask import Flask, jsonify, request, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# SQLite Database setup
conn = sqlite3.connect('study_sessions.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        end_time TEXT,
        subject TEXT,
        description TEXT,
        date DATE
    )
""")
conn.commit()

@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 5")
    recent_sessions = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(DISTINCT date) AS streak FROM sessions
        WHERE date >= date('now', '-10 days') AND date < date('now')
    """)
    streak = cursor.fetchone()[0] or 0

    return render_template('index.html', recent_sessions=recent_sessions, streak=streak)

@app.route('/log', methods=['POST'])
def log_session():
    data = request.json
    start = data.get('start')
    end = data.get('end')
    subject = data.get('subject')
    description = data.get('description')
    print(description)
    date = datetime.now().strftime('%Y-%m-%d')

    if not start or not end or not subject:
        return jsonify({'message': 'Invalid data!'}), 400

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (start_time, end_time, subject, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, (start, end, subject, description, date))
    conn.commit()

    return jsonify({'message': 'Study session logged successfully!'})

@app.route('/get_sessions', methods=['GET'])
def get_sessions():
    cursor = conn.cursor()

    # Fetch recent sessions
    cursor.execute("""
        SELECT start_time, end_time, subject, description, date FROM sessions
        ORDER BY id DESC LIMIT 5
    """)
    recent_sessions = cursor.fetchall()

    # Calculate streak
    cursor.execute("""
        SELECT date FROM sessions
        GROUP BY date
        ORDER BY date DESC
    """)
    dates = [row[0] for row in cursor.fetchall()]

    streak = 0
    for i, session_date in enumerate(dates):
        if i == 0 or (datetime.strptime(dates[i - 1], '%Y-%m-%d') - datetime.strptime(session_date, '%Y-%m-%d')).days == 1:
            streak += 1
        else:
            break

    return jsonify({'streak': streak, 'recent_sessions': recent_sessions})
@app.route('/all_sessions')
def all_sessions():
    # Fetch all sessions from the database
    conn = sqlite3.connect('study_sessions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT start_time, end_time, subject, description, date FROM sessions ORDER BY date DESC, start_time DESC')
    sessions = cursor.fetchall()
    conn.close()

    # Render the 'all_sessions.html' template and pass the sessions
    return render_template('all_sessions.html', sessions=sessions)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no PORT environment variable is set
    app.run(host="0.0.0.0", port=port)
