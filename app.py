from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'render_quiz_secret_9981'
# Allow connections from anywhere on the web
socketio = SocketIO(app, cors_allowed_origins="*")

# 📋 INPUT YOUR QUESTIONS HERE
# 'options' is a list, 'correct' is the index of the right answer (0, 1, 2, or 3)
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "correct": 1
    },
    {
        "question": "What is 5 + 7?",
        "options": ["10", "11", "12", "13"],
        "correct": 2
    }
]

leaderboard = {} # Keeps track of { username: score }

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_game')
def handle_join(data):
    username = data.get('username')
    if username:
        leaderboard[username] = 0
        print(f"🎮 Player {username} connected from the cloud!")
        emit('start_quiz', {"questions": QUESTIONS})

@socketio.on('submit_score')
def handle_score(data):
    username = data.get('username')
    answers = data.get('answers')
    
    if not username or not answers:
        return

    # Calculate score against the QUESTIONS array
    score = 0
    for i, q in enumerate(QUESTIONS):
        if i < len(answers) and answers[i] == q['correct']:
            score += 1
            
    leaderboard[username] = score
    
    # Sort leaderboard from highest score to lowest
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    # Reply back to user with their score, tell everyone to update leaderboard
    emit('quiz_results', {"score": score, "total": len(QUESTIONS)})
    emit('update_leaderboard', {"leaderboard": sorted_leaderboard}, broadcast=True)

if __name__ == '__main__':
    # Local fallback testing
    socketio.run(app)