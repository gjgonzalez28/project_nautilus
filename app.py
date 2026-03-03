#!/usr/bin/env python
"""
Project Nautilus: Flask API Server with NeMo Guardrails Integration

This is the main entry point for the diagnostic system.
- Flask handles HTTP requests
- NeMo Guardrails handles conversation logic and state
- Python utilities provide fuzzy matching, API calls, validation
"""

import os
import json
import logging
import warnings
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from app_logging.logger import setup_logging, StructuredLogger
from app_logging.cost_monitor import estimate_api_cost
from nemoguardrails import LLMRails, RailsConfig

# Load environment variables
load_dotenv()

# Initialize logging
proj_root = Path(__file__).parent
log_dir = proj_root / "logs"
log_dir.mkdir(exist_ok=True)
setup_logging(log_dir=str(log_dir))

# Reduce noisy warnings from langchain google integration.
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
warnings.filterwarnings(
    "ignore",
    message="WARNING! stream_usage is not default parameter.",
)

logger = StructuredLogger(__name__)

# Initialize Flask
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# ============================================================================
# NeMo Guardrails Initialization
# ============================================================================

def initialize_nemo():
    """
    Load NeMo Guardrails configuration and initialize LLMRails instance.
    
    Returns:
        LLMRails instance or None if initialization fails
    """
    try:
        nemo_config_path = os.getenv('NEMO_CONFIG_PATH', './config/rails')
        
        logger.log_event(
            event="nemo_initialization",
            data={"config_path": nemo_config_path},
            component="nemo_init"
        )
        
        # Load configuration from YAML
        config = RailsConfig.from_path(nemo_config_path)
        
        # Create LLMRails instance
        rails = LLMRails(config)
        
        logger.log_event(
            event="nemo_loaded",
            data={"status": "success"},
            component="nemo_init"
        )
        
        return rails
        
    except Exception as e:
        logger.log_event(
            event="nemo_initialization_failed",
            data={"error": str(e)},
            component="nemo_init"
        )
        print(f"❌ Failed to initialize NeMo: {e}")
        return None


def run_async(coro):
    """Run an async coroutine on a dedicated event loop."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


# Initialize NeMo on startup
nemo_rails = initialize_nemo()

if nemo_rails:
    print("✅ NeMo Guardrails loaded successfully")
else:
    print("⚠️  NeMo initialization failed - some endpoints may not work")


# ============================================================================
# Global Sessions (In-memory for Phase 2, upgrade to SQLite in Phase 4)
# ============================================================================

sessions = {}


# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with web UI for testing"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Nautilus</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .status {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #4ade80;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
            }
            input, textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.2s;
            }
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                resize: vertical;
                min-height: 100px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                font-size: 14px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102,126,234,0.3);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .response-section {
                margin-top: 30px;
                display: none;
            }
            .response-section.show {
                display: block;
            }
            .response-header {
                font-weight: 600;
                color: #333;
                margin-bottom: 12px;
            }
            .response-box {
                background: #f5f5f5;
                border-left: 4px solid #667eea;
                padding: 16px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
                white-space: pre-wrap;
                word-break: break-word;
                max-height: 300px;
                overflow-y: auto;
            }
            .error {
                border-left-color: #ef4444;
                background: #fef2f2;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #667eea;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 0.6s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Project Nautilus</h1>
            <div class="status">
                <div class="status-dot"></div>
                <span>API Status: <strong>Running</strong></span>
            </div>
            
            <form id="diagnoseForm">
                <div class="form-group">
                    <label for="message">Diagnostic Message</label>
                    <textarea id="message" name="message" placeholder="Describe your issue..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="traceId">Session ID (optional)</label>
                    <input type="text" id="traceId" name="traceId" placeholder="Leave blank for new session">
                </div>
                
                <button type="submit" id="submitBtn">Send Message</button>
            </form>
            
            <div id="responseSection" class="response-section">
                <div class="response-header">Response:</div>
                <div id="responseBox" class="response-box"></div>
            </div>
        </div>
        
        <script>
            const form = document.getElementById('diagnoseForm');
            const submitBtn = document.getElementById('submitBtn');
            const responseSection = document.getElementById('responseSection');
            const responseBox = document.getElementById('responseBox');
            const messageInput = document.getElementById('message');
            const traceIdInput = document.getElementById('traceId');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const message = messageInput.value.trim();
                const traceId = traceIdInput.value.trim();
                
                if (!message) {
                    alert('Please enter a message');
                    return;
                }
                
                submitBtn.disabled = true;
                responseBox.innerHTML = '<div class="loading"><div class="spinner"></div> Processing...</div>';
                responseSection.classList.add('show');
                
                try {
                    const payload = { message };
                    if (traceId) payload.trace_id = traceId;
                    
                    const response = await fetch('/diagnose', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const formatted = `Response:\\n${data.response}\\n\\nTrace ID: ${data.trace_id}\\nTurn: ${data.turn}`;
                        responseBox.textContent = formatted;
                        responseBox.classList.remove('error');
                        
                        // Update trace ID for next message
                        traceIdInput.value = data.trace_id;
                    } else {
                        const error = data.error || 'Unknown error';
                        const details = data.details ? `\\nDetails: ${data.details}` : '';
                        responseBox.textContent = `Error: ${error}${details}`;
                        responseBox.classList.add('error');
                    }
                } catch (err) {
                    responseBox.textContent = `Network Error: ${err.message}`;
                    responseBox.classList.add('error');
                } finally {
                    submitBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "available",
        "version": "2.0",
        "phase": "Phase 2: NeMo Setup",
        "nemo_status": "loaded" if nemo_rails else "failed"
    }), 200


@app.route('/diagnose', methods=['POST'])
def diagnose():
    """
    Main diagnostic endpoint.
    
    Accepts:
    {
        "message": "The screen is black",
        "trace_id": "optional_session_id"
    }
    
    Returns:
    {
        "response": "Let's work through this...",
        "trace_id": "conv_abc123",
        "turn": 1
    }
    """
    try:
        if not nemo_rails:
            return jsonify({
                "error": "NeMo Guardrails not available",
                "details": "Check server initialization logs"
            }), 503
        
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        trace_id = data.get('trace_id')
        
        if not user_message:
            return jsonify({
                "error": "Message required",
                "format": {"message": "string (required)", "trace_id": "string (optional)"}
            }), 400
        
        # Create new session if needed
        if not trace_id or trace_id not in sessions:
            trace_id = logger.set_trace_id()
            sessions[trace_id] = {
                "turns": 0,
                "messages": []
            }
        
        session = sessions[trace_id]
        session["turns"] += 1
        
        # Log this turn
        logger.log_event(
            event="user_message",
            data={
                "turn": session["turns"],
                "message": user_message
            },
            component="flask_api"
        )
        
        # Estimate cost before API call
        print(f"\n[Turn {session['turns']}] Estimating cost for Gemini API call...")
        estimate_api_cost(
            input_text=user_message,
            output_estimate="~500 tokens (typical response)"
        )
        
        # Process through NeMo Guardrails
        print(f"[Turn {session['turns']}] Sending to NeMo/Gemini...")
        response = run_async(
            nemo_rails.generate_async(
                messages=[{"role": "user", "content": user_message}]
            )
        )
        
        # Extract response text
        bot_message = response.get("content", "") if isinstance(response, dict) else str(response)
        
        # Log response
        logger.log_event(
            event="assistant_message",
            data={
                "turn": session["turns"],
                "response": bot_message
            },
            component="flask_api"
        )
        
        # Store in session
        session["messages"].append({
            "role": "user",
            "content": user_message
        })
        session["messages"].append({
            "role": "assistant",
            "content": bot_message
        })
        
        return jsonify({
            "response": bot_message,
            "trace_id": trace_id,
            "turn": session["turns"]
        }), 200
        
    except Exception as e:
        logger.log_event(
            event="error",
            data={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "endpoint": "/diagnose"
            },
            component="flask_api"
        )
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if os.getenv('FLASK_ENV') == 'development' else None
        }), 500


@app.route('/session/<trace_id>', methods=['GET'])
def get_session(trace_id: str):
    """Get current session state"""
    if trace_id not in sessions:
        return jsonify({
            "error": "Session not found",
            "trace_id": trace_id
        }), 404
    
    session = sessions[trace_id]
    return jsonify({
        "trace_id": trace_id,
        "turns": session["turns"],
        "messages": session["messages"]
    }), 200


@app.route('/session/<trace_id>', methods=['DELETE'])
def end_session(trace_id: str):
    """End a session"""
    if trace_id in sessions:
        del sessions[trace_id]
        logger.log_event(
            event="session_ended",
            data={"trace_id": trace_id},
            component="flask_api"
        )
        return jsonify({
            "status": "session_ended",
            "trace_id": trace_id
        }), 200
    else:
        return jsonify({
            "error": "Session not found",
            "trace_id": trace_id
        }), 404


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET  /health",
            "POST /diagnose",
            "GET  /session/<trace_id>",
            "DELETE /session/<trace_id>"
        ]
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.log_event(
        event="server_error",
        data={"error": str(error)},
        component="flask"
    )
    return jsonify({
        "error": "Internal server error"
    }), 500


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.log_event(
        event="app_started",
        data={
            "port": port,
            "debug_mode": debug,
            "phase": "Phase 2: NeMo Setup",
            "nemo_available": nemo_rails is not None
        },
        component="main"
    )
    
    print("\n" + "="*70)
    print("PROJECT NAUTILUS: Flask API + NeMo Guardrails")
    print("="*70)
    print(f"🚀 Starting on http://localhost:{port}")
    print(f"📝 Logs: {log_dir}/")
    print(f"⚙️  NeMo Config: {os.getenv('NEMO_CONFIG_PATH', './config/rails')}")
    print("\nAvailable Endpoints:")
    print(f"  GET  /health           - Health check")
    print(f"  POST /diagnose         - Send diagnostic message")
    print(f"  GET  /session/<id>     - View session state")
    print(f"  DELETE /session/<id>   - End session")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)


