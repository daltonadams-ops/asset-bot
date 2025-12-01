import os
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
EXCEL_FILE = 'assets.xlsx'

def find_employee_in_excel(name_query):
    """
    Reads the Excel file and searches for a name.
    Returns a LIST of dictionaries (one for each row found).
    """
    if not os.path.exists(EXCEL_FILE):
        return "ERROR_FILE_NOT_FOUND"

    try:
        # Load the Excel file
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        
        # Clean headers
        df.columns = df.columns.str.strip().str.lower()
        
        # Find name column
        possible_name_cols = ['name', 'employee', 'user', 'full name', 'assigned to']
        name_col = next((col for col in possible_name_cols if col in df.columns), None)

        if not name_col:
            return "ERROR_NO_NAME_COL"

        # Search for ALL matches
        # We verify that the name matches exactly (case-insensitive)
        matches = df[df[name_col].astype(str).str.strip().str.lower() == name_query.lower()]

        if matches.empty:
            return []
        
        # Convert ALL matching rows to a list of dictionaries
        # orient='records' creates a list like: [{row1}, {row2}, {row3}]
        return matches.fillna('').to_dict(orient='records')

    except Exception as e:
        print(f"Excel Error: {e}")
        return "ERROR_READING_FILE"

@app.route('/', methods=['GET'])
def home():
    return "Excel Asset Bot is Alive (Multi-Device Supported)!", 200

@app.route('/asset', methods=['POST'])
def asset_lookup():
    data = request.form
    user_query = data.get('text', '').strip()
    
    if not user_query:
         return jsonify({
            "response_type": "ephemeral",
            "text": "⚠️ Please type a name. Example: `/asset John Smith`"
        })

    # --- Logic: Find All Assets ---
    results = find_employee_in_excel(user_query)

    # --- Error Handling ---
    if results == "ERROR_FILE_NOT_FOUND":
        return jsonify({"response_type": "ephemeral", "text": "⚠️ Server Error: `assets.xlsx` missing."})
    if results == "ERROR_NO_NAME_COL":
        return jsonify({"response_type": "ephemeral", "text": "⚠️ Data Error: No 'Name' column found."})
    if results == "ERROR_READING_FILE":
         return jsonify({"response_type": "ephemeral", "text": "⚠️ System Error: Could not read Excel file."})

    # If list is empty
    if not results:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Could not find any assets assigned to *'{user_query}'*."
        })

    # --- Success: Build the Slack Card ---
    # We start with a header
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"💻 Asset Lookup: {user_query.title()} ({len(results)} items)",
                "emoji": True
            }
        }
    ]

    skip_cols = ['name', 'employee', 'user', 'full name', 'assigned to']

    # Loop through EVERY matching row found
    for index, asset_row in enumerate(results):
        
        # Add a divider line between devices (but not before the first one)
        if index > 0:
            blocks.append({"type": "divider"})

        fields = []
        for key, value in asset_row.items():
            if key not in skip_cols and str(value).strip() != '':
                formatted_key = key.replace('_', ' ').title()
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{formatted_key}:*\n{value}"
                })
        
        # Add the section for this specific device
        # (Slack limits fields to 10 per section)
        if fields:
            blocks.append({
                "type": "section",
                "fields": fields[:10] 
            })
        else:
            # Fallback if a row has a name but no other data
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "_No additional details for this entry._"}
            })

    return jsonify({
        "response_type": "in_channel",
        "blocks": blocks
    })

if __name__ == '__main__':
    print("------------------------------------------------")
    print("🤖 Bot is listening on http://localhost:3000")
    print("------------------------------------------------")
    app.run(port=3000, debug=True)
