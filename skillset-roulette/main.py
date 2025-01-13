import os, sys
import queue  # Import queue for thread-safe operations

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if (parent_dir not in sys.path):
    sys.path.append(parent_dir)

import json
from flask import Flask, request, jsonify, render_template, Response
from app import RouletteGame
from utils.log_utils import *
import utils.github_utils as github_utils

logger = configure_logger(with_date_folder=False)
logger.info('-----------------Starting-----------------')

verify_request_from_GitHub = True

# Debug users not saved to historical records, can play multiple times
debug_users = [
    "satomic",
]  

# Define the path to store historical records
HISTORY_FILE = "logs/history.json"

# Create Flask app
app = Flask(__name__)

# Prize list
PRIZES_JSON = "prizes.json"

def _load_prizes():
    if os.path.exists(PRIZES_JSON):
        with open(PRIZES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

prize_dict = _load_prizes()
game = RouletteGame(prize_dict)

# Load historical player records
def _load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

player_history = _load_history()

def load_history():
    """Load historical records, initialize to empty if not exist"""
    global player_history
    if not os.path.exists("logs"):
        os.makedirs("logs")  # Create logs folder

    player_history = _load_history()
    logger.info("Historical records loaded")

def save_history():
    """Save historical records to file"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(player_history, f, ensure_ascii=False, indent=4)
    logger.info("Historical records saved")

# Replace the global 'subscribers' queue with a list of queues, one per client
subscribers = []

def notify_spin(player_name, result):
    """Push spin result and full winners list via SSE to all subscribers"""
    spin_event = {
        "name": player_name,         # Current player's name
        "result": result,            # Current winning prize
        "winners": game.get_winners()  # Full winners list
    }
    for q in subscribers:
        q.put(spin_event)  # Send to each client's queue
    logger.info(f"Notify spin: {player_name} - {result} - Total Subscribers: {len(subscribers)}")

@app.route("/")
def index():
    logger.info("Load homepage")
    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play():
    if request.method == 'POST':

        data = request.get_json()
        player_message = data.get("message", "")

        github_handler = github_utils.GitHubHandler(request)
        if verify_request_from_GitHub:
            if not github_handler.verify_github_signature():
                return jsonify({"error": "Request must be from GitHub"}), 403

        user_login = github_handler.get_user_login()
        player_name = user_login
        if not player_name:
            logger.warning("not from GitHub")
            player_name = data.get("name")

        
        logger.info(f"Player '{player_name}' message: {player_message}")

        if not player_name:
            logger.warning("Player name is empty")
            return jsonify({"error": "Player name is required"}), 400

        # Check if the player has already played
        if player_name in player_history:
            logger.warning(f"Player '{player_name}' has already played")
            return jsonify({"error": f"Player '{player_name}' has already played and cannot play again!"}), 403

        # Player has not played, execute roulette spin logic
        result = game.spin(player_name)
        logger.info(f"Player '{player_name}' spin result: {result}")

        
        if player_name not in debug_users: # debug
            # Save to historical records
            player_history[player_name] = result
            save_history()  # Persist save

        # Notify SSE and return result
        notify_spin(player_name, result)
        return jsonify({"result": result})

    return jsonify({"status": "ok"})

@app.route("/winners_stream")
def winners_stream():
    """SSE route to push spin events and winners list to the browser"""
    def stream():
        q = queue.Queue()
        subscribers.append(q)
        logger.info(f"New SSE client connected. Total Subscribers: {len(subscribers)}")
        try:
            while True:
                try:
                    spin_event = q.get(timeout=1)  # Blocking get with timeout
                    yield f"data: {json.dumps(spin_event, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    pass  # No spin event available, continue looping
        finally:
            subscribers.remove(q)
            logger.info(f"SSE client disconnected. Total Subscribers: {len(subscribers)}")

    logger.info("SSE connection established")
    return Response(stream(), content_type="text/event-stream")

def sync_game_winners():
    """Sync historical records to RouletteGame instance"""
    game.winners = []
    for name, prize in player_history.items():
        if prize != game.thanks:
            game.winners.append({"name": name, "prize": prize})
    logger.info("Historical records synced to game instance")

@app.route("/winners")
def get_winners():
    sync_game_winners()
    return jsonify(game.get_winners())

@app.route("/prizes")
def get_prizes():
    """Return prize-to-color mapping"""
    return jsonify(prize_dict)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    response.headers["ETag"] = ""
    response.headers["X-Accel-Buffering"] = "no"
    return response

def notify_winners():
    """Push winners list to all subscribers"""
    while not subscribers.empty():
        subscriber = subscribers.get()
        logger.info(f"Notify subscriber: {subscriber}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, threaded=True)