"""
Project Nautilus: Flask API Server

Starts on 0.0.0.0:5000 (or $PORT environment variable)
Serves index.html chat UI and /ask endpoint for diagnostics
"""

from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# Simple CORS support without external dependency
@app.after_request
def enable_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Attempt to import backend, but don't fail if it's unavailable
_backend_available = False
try:
    from chatgpt_integration import nautilus_ask
    _backend_available = True
    print("[INIT] Nautilus backend loaded successfully")
except ImportError as e:
    print(f"[INIT] Warning - Nautilus backend not available: {e}")
except Exception as e:
    print(f"[INIT] Error loading Nautilus backend: {e}")


@app.route('/', methods=['GET'])
def index():
    """Serve the chat UI."""
    return send_from_directory('.', 'index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Nautilus API running",
        "backend": "enabled" if _backend_available else "disabled"
    })


@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    """Handle diagnostic questions."""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json or {}
        user_message = data.get('user_message', '').strip()
        
        if not user_message:
            return jsonify({
                "error": "user_message required",
                "response": "Please describe your machine issue."
            }), 400
        
        # Try to use backend if available
        if _backend_available:
            try:
                result = nautilus_ask(user_message)
                return jsonify(result), 200
            except Exception as e:
                print(f"[ERROR] nautilus_ask failed: {e}")
                return jsonify({
                    "error": f"Backend error: {str(e)}",
                    "response": "I encountered an error. Please try again."
                }), 500
        else:
            # Fallback: return echo response
            return jsonify({
                "response": f"Echo (backend unavailable): {user_message}",
                "note": "Nautilus backend not loaded. Check server logs."
            }), 200
            
    except Exception as e:
        print(f"[ERROR] /ask handler error: {e}")
        return jsonify({
            "error": str(e),
            "response": "Server error processing your message."
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', '').lower() == 'development'
    
    print("\n" + "="*70)
    print("PROJECT NAUTILUS - API SERVER")
    print("="*70)
    print(f"Port: {port} (HOST: 0.0.0.0)")
    print(f"Mode: {'Development' if debug else 'Production'}")
    print(f"Backend: {'Available' if _backend_available else 'Unavailable (UI-only fallback)'}")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

