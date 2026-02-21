"""
Project Nautilus: Flask API Server for ChatGPT Integration

Run this to start the local API server:
  python app.py

Then in another terminal, run:
  ngrok http 5000

Copy the ngrok URL into ChatGPT function definitions.
"""

from flask import Flask, request, jsonify, send_file
from chatgpt_integration import (
    initialize_session,
    nautilus_ask,
    nautilus_set_test_mode,
    nautilus_get_session_state,
    nautilus_end_session,
    nautilus_reset
)
import json
import os

app = Flask(__name__)

# Enable CORS for ChatGPT
from flask_cors import CORS
CORS(app)


@app.route('/', methods=['GET'])
def index():
    """Serve the chat UI."""
    return send_file('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Project Nautilus API is running"})


@app.route('/initialize', methods=['POST'])
def init_session():
    """Initialize a new session."""
    try:
        result = initialize_session()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask_nautilus():
    """Send message to Nautilus."""
    try:
        data = request.json
        user_message = data.get('user_message', '')
        
        if not user_message:
            return jsonify({"error": "user_message is required"}), 400
        
        result = nautilus_ask(user_message)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set-mode', methods=['POST'])
def set_mode():
    """Set test mode (beginner/intermediate/pro)."""
    try:
        data = request.json
        mode = data.get('mode', '').lower()
        
        if mode not in ['beginner', 'intermediate', 'pro']:
            return jsonify({"error": "mode must be beginner, intermediate, or pro"}), 400
        
        result = nautilus_set_test_mode(mode)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/state', methods=['GET'])
def get_state():
    """Get current session state."""
    try:
        result = nautilus_get_session_state()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/end-session', methods=['POST'])
def end_session():
    """End session and generate report."""
    try:
        result = nautilus_end_session()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reset', methods=['POST'])
def reset_session():
    """Reset session."""
    try:
        result = nautilus_reset()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PROJECT NAUTILUS: FLASK API SERVER")
    print("="*70)
    print("\nServer starting on http://localhost:5000")
    print("\nTo expose to ChatGPT, run in another terminal:")
    print("  ngrok http 5000")
    print("\nEndpoints:")
    print("  POST /initialize - Start new session")
    print("  POST /ask - Send message to Nautilus")
    print("  POST /set-mode - Set skill level (beginner/intermediate/pro)")
    print("  GET /state - Get current session state")
    print("  POST /end-session - End and generate report")
    print("  POST /reset - Reset session")
    print("  GET /health - Health check")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='localhost', port=5000)
