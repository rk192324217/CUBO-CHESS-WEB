from flask import Flask, render_template, request, jsonify
import chess
from engine import get_ai_move
import json
import os
from datetime import datetime

app = Flask(__name__, 
            static_folder="../frontend/static",
            template_folder="../frontend/templates")

def load_user_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "games": []}

def save_user_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def handle_move():
    data = request.json
    user_id = data.get("user_id", "guest")
    board = chess.Board(data["fen"])

    # Track user move
    if "move" in data:
        user_data = load_user_data()
        user_entry = user_data["users"].setdefault(user_id, {
            "total_moves": 0,
            "games_played": 0,
            "last_played": datetime.now().isoformat()
        })
        user_entry["total_moves"] += 1

        game_id = f"game_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        user_data["games"].append({
            "game_id": game_id,
            "user_id": user_id,
            "move": data["move"],
            "fen": data["fen"],
            "timestamp": datetime.now().isoformat(),
            "difficulty": data["difficulty"]
        })
        save_user_data(user_data)

    # Get AI move
    ai_move = get_ai_move(board, data["difficulty"], user_id)
    if not ai_move:
        return jsonify({"error": "No legal moves"}), 400

    board.push(ai_move)

    # If AI just moved into a checkmate, log the mistake
    if board.is_checkmate():
        mistake_entry = {
            "user_id": user_id,
            "fen": data["fen"],
            "move": ai_move.uci(),
            "timestamp": datetime.now().isoformat()
        }
        with open("mistakes.json", "a") as f:
            f.write(json.dumps(mistake_entry) + "\n")

    return jsonify({
        "move": ai_move.uci(),
        "fen": board.fen(),
        "is_checkmate": board.is_checkmate(),
        "is_draw": (
            board.is_stalemate() or
            board.is_insufficient_material() or
            board.can_claim_fifty_moves() or
            board.can_claim_threefold_repetition()
        )
    })

if __name__ == "__main__":
    if not os.path.exists("user_data.json"):
        with open("user_data.json", "w") as f:
            json.dump({"users": {}, "games": []}, f)
    app.run(debug=True, port=5000)
