#!/usr/bin/env python3
"""
Test HTTP service with Basic Authentication
For testing DocuSign Workflow Builder's "Make a Web Request" step
"""

from flask import Flask, request, jsonify
from functools import wraps
import base64
import os
from datetime import datetime

app = Flask(__name__)

# Test credentials
VALID_USERNAME = "docusign_test"
VALID_PASSWORD = "test_password_123"

def check_auth(username, password):
    """Check if username and password are valid."""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def authenticate(f):
    """Decorator for routes requiring Basic Auth."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization

        if not auth:
            return jsonify({
                "error": "Missing Authorization header",
                "message": "Please provide Basic Authentication credentials"
            }), 401

        if not check_auth(auth.username, auth.password):
            return jsonify({
                "error": "Invalid credentials",
                "message": f"Authentication failed for username: {auth.username}"
            }), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no auth required)."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DocuSign Workflow Test Service"
    }), 200

@app.route('/api/test', methods=['GET', 'POST'])
@authenticate
def test_endpoint():
    """Protected endpoint - requires Basic Auth."""
    return jsonify({
        "status": "success",
        "message": "Authentication successful!",
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "authenticated_user": request.authorization.username
    }), 200

@app.route('/api/process', methods=['POST'])
@authenticate
def process_endpoint():
    """Protected endpoint that echoes back the request data."""
    data = request.get_json() if request.is_json else {}

    return jsonify({
        "status": "success",
        "message": "Request processed successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "received_data": data,
        "headers_received": {k: v for k, v in request.headers.items() if k.lower() != 'authorization'}
    }), 200

@app.route('/api/echo', methods=['POST'])
@authenticate
def echo_endpoint():
    """Protected endpoint that echoes back request details."""
    return jsonify({
        "status": "success",
        "echo": {
            "method": request.method,
            "path": request.path,
            "content_type": request.content_type,
            "data": request.get_json() if request.is_json else request.data.decode() if request.data else None,
            "authenticated_as": request.authorization.username
        },
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/credentials', methods=['GET'])
def get_credentials():
    """Get test credentials (no auth required - informational only)."""
    return jsonify({
        "credentials": {
            "username": VALID_USERNAME,
            "password": VALID_PASSWORD
        },
        "note": "Use these credentials for Basic Auth in DocuSign Workflow Builder",
        "endpoints": {
            "health_check": "/health",
            "test": "/api/test",
            "process": "/api/process",
            "echo": "/api/echo"
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "GET /health",
            "GET /api/credentials",
            "GET /api/test (requires auth)",
            "POST /api/test (requires auth)",
            "POST /api/process (requires auth)",
            "POST /api/echo (requires auth)"
        ]
    }), 404

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    print("\n" + "="*60)
    print("TEST HTTP SERVICE - DocuSign Workflow Builder")
    print("="*60)
    print("\nTest Credentials:")
    print(f"  Username: {VALID_USERNAME}")
    print(f"  Password: {VALID_PASSWORD}")
    print("\nEndpoints:")
    print("  GET  /health              - Health check (no auth)")
    print("  GET  /api/credentials     - Show test credentials (no auth)")
    print("  GET  /api/test            - Test endpoint (requires auth)")
    print("  POST /api/test            - Test endpoint (requires auth)")
    print("  POST /api/process         - Process data (requires auth)")
    print("  POST /api/echo            - Echo request (requires auth)")
    print("\nUsage in DocuSign Workflow Builder:")
    print("  1. Add 'Make a Web Request' step")
    print(f"  2. Set URL: https://your-public-url/api/test")
    print("  3. Set Auth Type: Basic Authentication")
    print(f"  4. Username: {VALID_USERNAME}")
    print(f"  5. Password: {VALID_PASSWORD}")
    print("\n" + "="*60)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("="*60 + "\n")

    app.run(debug=False, host='0.0.0.0', port=port)
