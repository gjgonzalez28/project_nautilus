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

# Runtime API key storage (can be set via /api/set-key endpoint)
runtime_config = {
    "openai_api_key": os.getenv('OPENAI_API_KEY')
}


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
        # Use runtime API key if provided, otherwise fall back to environment
        if runtime_config.get("openai_api_key"):
            os.environ['OPENAI_API_KEY'] = runtime_config["openai_api_key"]
        
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
    """Root endpoint with chat-style web UI"""
    html = r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Nautilus - Diagnostic Assistant</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                padding: 20px;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
                width: 100%;
                max-width: 800px;
                margin: auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                height: 85vh;
                overflow: hidden;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid #e0e0e0;
                position: relative;
            }
            .settings-btn {
                position: absolute;
                right: 20px;
                top: 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.2s;
            }
            .settings-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }
            .modal.open {
                display: flex;
            }
            .modal-content {
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            .modal-header {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 20px;
                color: #333;
            }
            .modal-field {
                margin-bottom: 20px;
            }
            .modal-label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
                font-size: 14px;
            }
            .modal-input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                font-family: monospace;
            }
            .modal-input:focus {
                outline: none;
                border-color: #667eea;
            }
            .modal-buttons {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            .modal-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 13px;
                transition: opacity 0.2s;
            }
            .modal-btn-save {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .modal-btn-save:hover {
                opacity: 0.9;
            }
            .modal-btn-cancel {
                background: #f0f0f0;
                color: #333;
            }
            .modal-btn-cancel:hover {
                background: #e0e0e0;
            }
            .chat-header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            .chat-status {
                font-size: 12px;
                opacity: 0.9;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4ade80;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; } 50% { opacity: 0.5; }
            }
            .messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            .message {
                display: flex;
                gap: 12px;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user {
                justify-content: flex-end;
            }
            .message-bubble {
                max-width: 65%;
                padding: 12px 16px;
                border-radius: 12px;
                line-height: 1.4;
                font-size: 14px;
                word-wrap: break-word;
            }
            .user .message-bubble {
                background: #667eea;
                color: white;
                border-bottom-right-radius: 4px;
            }
            .assistant .message-bubble {
                background: #f0f0f0;
                color: #333;
                border-bottom-left-radius: 4px;
            }
            .error .message-bubble {
                background: #fef2f2;
                color: #dc2626;
                border-left: 3px solid #dc2626;
            }
            .loading {
                display: flex;
                gap: 4px;
                align-items: center;
            }
            .loading-dot {
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: bounce 1.4s infinite;
            }
            .loading-dot:nth-child(2) { animation-delay: 0.2s; }
            .loading-dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes bounce {
                0%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
            }
            .input-area {
                border-top: 1px solid #e0e0e0;
                padding: 16px;
                background: #fafafa;
            }
            .input-form {
                display: flex;
                gap: 12px;
            }
            input {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.2s;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102,126,234,0.3);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .empty-state {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: #999;
                text-align: center;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <button class="settings-btn" id="settingsBtn">⚙️ Settings</button>
                <h1>🚀 Project Nautilus</h1>
                <div class="chat-status">
                    <div class="status-dot"></div>
                    Diagnostic Assistant
                </div>
            </div>
            
            <div class="messages" id="messagesContainer">
                <div class="empty-state">
                    <div>
                        <p style="margin-bottom: 10px;">Welcome to Project Nautilus</p>
                        <p style="font-size: 12px; color: #bbb;">Describe your issue and I'll help diagnose it</p>
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <form class="input-form" id="chatForm">
                    <input type="text" id="messageInput" placeholder="Describe your issue..." required autocomplete="off">
                    <button type="submit" id="sendBtn">Send</button>
                </form>
            </div>
        </div>
        
        <div class="modal" id="settingsModal">
            <div class="modal-content">
                <div class="modal-header">Configure API Key</div>
                <div class="modal-field">
                    <label class="modal-label">OpenAI API Key (sk-...)</label>
                    <input type="password" class="modal-input" id="apiKeyInput" placeholder="Paste your OpenAI API key here">
                </div>
                <div style="margin-bottom: 20px; font-size: 12px; color: #666;">
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" style="color: #667eea;">OpenAI Platform</a>
                </div>
                <div class="modal-buttons">
                    <button class="modal-btn modal-btn-cancel" id="cancelBtn">Cancel</button>
                    <button class="modal-btn modal-btn-save" id="saveBtn">Save & Initialize</button>
                </div>
            </div>
        </div>
        
        <script>
            const form = document.getElementById('chatForm');
            const input = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const container = document.getElementById('messagesContainer');
            let sessionId = null;
            let isLoading = false;
            
            function addMessage(text, sender, isError = false) {
                if (container.querySelector('.empty-state')) {
                    container.innerHTML = '';
                }
                const msg = document.createElement('div');
                msg.className = 'message ' + sender + (isError ? ' error' : '');
                msg.innerHTML = '<div class="message-bubble">' + escapeHtml(text) + '</div>';
                container.appendChild(msg);
                container.scrollTop = container.scrollHeight;
            }
            
            function addLoadingMessage() {
                if (container.querySelector('.empty-state')) {
                    container.innerHTML = '';
                }
                const msg = document.createElement('div');
                msg.className = 'message assistant';
                msg.id = 'loadingMsg';
                msg.innerHTML = '<div class="message-bubble"><div class="loading"><div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div></div></div>';
                container.appendChild(msg);
                container.scrollTop = container.scrollHeight;
            }
            
            function removeLoadingMessage() {
                const loading = document.getElementById('loadingMsg');
                if (loading) loading.remove();
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                if (isLoading) return;
                
                const text = input.value.trim();
                if (!text) return;
                
                addMessage(text, 'user');
                input.value = '';
                isLoading = true;
                sendBtn.disabled = true;
                
                addLoadingMessage();
                
                try {
                    const payload = { message: text };
                    if (sessionId) payload.trace_id = sessionId;
                    
                    const response = await fetch('/diagnose', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    removeLoadingMessage();
                    
                    if (response.ok) {
                        addMessage(data.response, 'assistant');
                        sessionId = data.trace_id;
                    } else {
                        const error = data.details || data.error || 'Unknown error';
                        addMessage('Error: ' + error, 'assistant', true);
                    }
                } catch (err) {
                    removeLoadingMessage();
                    addMessage('Network error: ' + err.message, 'assistant', true);
                } finally {
                    isLoading = false;
                    sendBtn.disabled = false;
                    input.focus();
                }
            });
            
            document.addEventListener('DOMContentLoaded', () => input.focus());
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


@app.route('/api/set-key', methods=['POST'])
def set_api_key():
    """
    Set OpenAI API key at runtime.
    
    Accepts:
    {
        "api_key": "sk-..."
    }
    """
    global nemo_rails
    
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({"error": "API key required"}), 400
        
        # Store the key
        runtime_config['openai_api_key'] = api_key
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Reinitialize NeMo with the new key
        nemo_rails = initialize_nemo()
        
        if nemo_rails:
            return jsonify({
                "status": "success",
                "message": "API key configured and NeMo initialized"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "API key set but NeMo initialization failed. Check logs for details."
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


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
        print(f"\n[Turn {session['turns']}] Estimating cost for OpenAI API call...")
        estimate_api_cost(
            input_text=user_message,
            output_estimate="~500 tokens (typical response)"
        )
        
        # Process through NeMo Guardrails
        print(f"[Turn {session['turns']}] Sending to NeMo/OpenAI...")
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


