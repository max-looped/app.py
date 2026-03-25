import streamlit as st
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Roblox Outreach Tool", layout="centered")
st.title("Roblox Outreach Tool")

# --- GOOGLE SHEETS AUTHENTICATION ---
try:
    # Load the service account JSON string from secrets
    key_json_str = st.secrets["gcp_service_account"]["key"]
    key_dict = json.loads(key_json_str)

    # Fix the private key newlines and PEM formatting
    private_key = key_dict['private_key'].strip()
    private_key = private_key.replace('\\\\n', '\n').replace('\\n', '\n')
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        private_key = '-----BEGIN PRIVATE KEY-----\n' + private_key
    if not private_key.endswith('-----END PRIVATE KEY-----'):
        private_key = private_key + '\n-----END PRIVATE KEY-----'
    key_dict['private_key'] = private_key

    # Define scopes
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authorize and connect
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)

    # Connect to your sheet
    sheet_name = "YOUR SHEET NAME"  # <-- Replace with your sheet name
    sheet = client.open(sheet_name).sheet1

    st.success("✅ Google Sheets connected successfully!")
except KeyError:
    st.error("❌ 'gcp_service_account' or 'key' not found in Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to load credentials or connect to Google Sheets: {e}")
    st.stop()

# --- FUNCTIONS ---
def extract_game_id(link):
    match = re.search(r'/games/(\d+)', link)
    return match.group(1) if match else link.strip()

def load_data():
    try:
        data = sheet.get_all_records()
        return {str(row["game_id"]): row for row in data}
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

def save_entry(game_id, link, discord):
    try:
        sheet.append_row([game_id, link, discord])
    except Exception as e:
        st.error(f"Error saving entry: {e}")

def generate_message(link):
    return f"""Hey, I came across your game and it looks like a strong fit for what we’re currently targeting.

I work in acquisitions for Looped Gaming—we buy Roblox games or partner with developers to help scale them.

If you’d be open to either selling or working together, I’d be interested in having a quick chat.

You can check us out here: https://www.loopedgaming.com

(Game link: {link})
"""

# --- UI ---
st.subheader("Add New Game")
link_input = st.text_input("Game Link")
discord_input = st.text_input("Discord Username")

existing_data = load_data()
existing_ids = set(existing_data.keys())

if st.button("Check & Generate"):
    if not link_input.strip():
        st.error("Please enter a game link!")
    else:
        game_id = extract_game_id(link_input)

        display_text = f"{link_input} | Discord: {discord_input}"

        if game_id in existing_ids:
            st.error(f"⚠️ Duplicate: {display_text}")
            st.text_area("Message to Send", "", height=200)
        else:
            save_entry(game_id, link_input, discord_input)
            st.success(f"✅ New: {display_text}")

            message = generate_message(link_input)
            st.text_area("Message to Send", message, height=200)

# --- OPTIONAL: Live table of existing entries ---
st.subheader("Existing Games")
if existing_data:
    st.table([[row["game_id"], row.get("link",""), row.get("discord","")] for row in existing_data.values()])
else:
    st.write("No games added yet.")
