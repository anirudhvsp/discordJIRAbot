import json
from flask import Flask, request, jsonify
from urllib.parse import urlencode
import os

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
client_id = config["client_id"]
client_secret = config["client_secret"]
redirect_uri = config["redirect_uri"]
oauth2_base_url = config["oauth2_base_url"]

# Initialize Flask app
app = Flask(__name__)

# Process 2: Web Server for OAuth callback
@app.route('/')
def handle_callback():
    """Handle OAuth2 callback and capture state/code from the URL"""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return jsonify({"error": "Missing code or state parameter."}), 400

    # Verify the state (you can use the Manager here for state communication)
    user_id = None
    for user, data in user_tokens.items():
        if data["state"] == state:
            user_id = user
            break

    if user_id is None:
        return jsonify({"error": "Invalid state. Authentication failed."}), 400

    try:
        # Exchange the authorization code for an access token
        import requests
        token_url = f"{oauth2_base_url}/oauth/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            return jsonify({"error": "Authentication failed. Please try again."}), 400

        token_data = response.json()
        access_token = token_data.get("access_token")

        # Update the shared user_tokens dictionary with the access token
        user_tokens[user_id]["access_token"] = access_token
        return jsonify({"message": "Authentication successful! You can now return to Discord."})

    except Exception as e:
        return jsonify({"error": f"Error during authentication: {str(e)}"}), 500


# This is the function to run the Flask server
def run_server(user_token):
    global user_tokens 
    user_tokens = user_token
    app.run(host='localhost', port=8080)
