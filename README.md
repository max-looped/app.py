# Roblox Outreach Tool

A Streamlit app to manage outreach for Roblox games. Features:
- Google Sheets integration for storing game links and Discord usernames.
- Duplicate detection.
- Auto-generated outreach messages.
- Live table of existing games.

## Setup
1. Add your Google Service Account JSON to Streamlit Secrets under `[gcp_service_account]`.
2. Update `sheet_name` in `app.py` with your Google Sheet name.
3. Install dependencies from `requirements.txt`.
4. Run with `streamlit run app.py`.
