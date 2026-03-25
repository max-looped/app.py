import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Roblox Outreach Tool", layout="centered")
st.title("Roblox Outreach Tool")

# --- GOOGLE SHEETS AUTHENTICATION ---
# Load the JSON key from Streamlit secrets
key_json_str = st.secrets["gcp_service_account"]["key"]
key_dict = json.loads(key_json_str)
key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

# Define Google API scopes
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate
try:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
    client = gspread.authorize(creds)
    st.session_state.client = client  # Keep globally accessible
    st.success("✅ Connected to Google Sheets successfully!")
except Exception as e:
    st.error(f"❌ Failed to load credentials or connect to Google Sheets: {e}")
    st.stop()

# --- CONNECT TO SHEET ---
sheet_name = "game"  # <-- Replace with your actual sheet name
try:
    sheet = client.open(sheet_name).sheet1
except Exception as e:
    st.error(f"❌ Failed to open sheet '{sheet_name}': {e}")
    st.stop()

# --- FUNCTIONS ---
def extract_game_id(link):
    """Extract the game ID from a Roblox link"""
    match = re.search(r'/games/(\d+)', link)
    return match.group(1) if match else link.strip()

def load_data():
    """Load existing game IDs from Google Sheet"""
    try:
        data = sheet.get_all_records()
        return {str(row["game_id"]): row for row in data}
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

def save_entry(game_id, link, discord):
    """Save a new entry to Google Sheet"""
    try:
        sheet.append_row([game_id, link, discord])
    except Exception as e:
        st.error(f"Error saving entry: {e}")

def generate_message(link):
    """Generate outreach message"""
    return f"""Hey, I came across your game and it looks like a strong fit for what we’re currently targeting.

I work in acquisitions for Looped Gaming—we buy Roblox games or partner with developers to help scale them.

If you’d be open to either selling or working together, I’d be interested in having a quick chat.

You can check us out here: https://www.loopedgaming.com

(Game link: {link})
"""

# --- UI ---
link = st.text_input("Game Link")
discord = st.text_input("Discord Username")

existing_data = load_data()
existing_ids = set(existing_data.keys())

if st.button("Check & Generate"):
    if not link.strip():
        st.error("Please enter a game link!")
    else:
        game_id = extract_game_id(link)

        if game_id in existing_ids:
            st.error("⚠️ Duplicate detected")
        else:
            save_entry(game_id, link, discord)
            st.success("✅ New game added")

            message = generate_message(link)
            st.text_area("Message to Send", message, height=200)

# --- LIVE TABLE OF EXISTING ENTRIES ---
st.subheader("Existing Games")
if existing_data:
    st.table([[row["game_id"], row.get("link", ""), row.get("discord", "")]
              for row in existing_data.values()])
else:
    st.write("No games added yet.")
