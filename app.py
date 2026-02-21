from flask import Flask, request, jsonify, send_from_directory
import json
import os
import sys

app = Flask(__name__, static_folder='.', static_url_path='')

# Enable CORS
from flask_cors import CORS
CORS(app)

# Lazy load backend to allow server to start even if backend has issues
_nautilus_session = None

def get_nautilus():
    """Lazy load nautilus backend."""
    global _nautilus_session
    if _nautilus_session is None:
        try:
            from chatgpt_integration import NautilusManager
            _nautilus_session = NautilusManager()
        except Exception as e:
            print(f"Warning: Could not load Nautilus backend: {e}")
            return None
    return _nautilus_session


@app.route('/', methods=['GET'])
def index():
    """Serve the chat UI."""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        return f"Error loading index.html: {e}", 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Project Nautilus API is running"})


@app.route('/ask', methods=['POST'])
def ask_nautilus():
    """Send message to Nautilus."""
    try:
        data = request.json
        user_message = data.get('user_message', '')
        
        if not user_message:
            return jsonify({"error": "user_message is required"}), 400
        
        try:
            from chatgpt_integration import nautilus_ask
            result = nautilus_ask(user_message)
            return jsonify(result), 200
        except Exception as e:
            print(f"Error calling nautilus_ask: {e}")
            return jsonify({"error": str(e), "response": "Backend error. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("\n" + "="*70)
    print("PROJECT NAUTILUS: FLASK API SERVER")
    print("="*70)
    print(f"\nServer starting on 0.0.0.0:{port}")
    print("\nEndpoints:")
    print("  GET / - Chat UI")
    print("  POST /ask - Send message to Nautilus")
    print("  GET /health - Health check")
    print("\n" + "="*70 + "\n")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)

