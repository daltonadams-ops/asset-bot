import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------
# MOCK DATABASE
# ---------------------------------------------------------------------
asset_database = {
    "sarah connor": {
        "laptop": "MacBook Pro 16 (M3 Max)",
        "serial": "SC-992-X",
        "monitor": "Dell UltraSharp 27",
        "last_audit": "2023-11-15"
    },
    "john smith": {
        "laptop": "Dell XPS 15",
        "serial": "JS-554-Y",
        "monitor": "None",
        "last_audit": "2024-01-10"
    }
}

@app.route('/', methods=['GET'])
def home():
    """Health check to see if bot is running in browser"""
    return "Asset Bot is Alive!", 200

@app.route('/asset', methods=['POST'])
def asset_lookup():
    data = request.form
    user_query = data.get('text', '').strip().lower()
    
    print(f"Incoming request for: {user_query}") # Debug print

    asset_info = asset_database.get(user_query)

    if not asset_info:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Could not find any assets assigned to '{user_query}'."
        })

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"💻 *Asset Data: {user_query.title()}*\nDevice: {asset_info['laptop']}\nSerial: `{asset_info['serial']}`"
            }
        }
    ]

    return jsonify({
        "response_type": "in_channel",
        "blocks": blocks
    })

if __name__ == '__main__':
    # Running on port 3000
    print("------------------------------------------------")
    print("🤖 Bot is listening on http://localhost:3000")
    print("------------------------------------------------")
    app.run(port=3000, debug=True)