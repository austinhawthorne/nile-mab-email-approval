import requests
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

API_URL = os.getenv("API_URL") + "/v1/settings/segments"
HEADERS = {"x-nile-api-key": os.getenv("X_NILE_API_KEY")}

def fetch_segments():
    """Fetch segment data from the API."""
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()

    try:
        data = response.json()

        # Ensure "data" key exists and contains "content"
        if isinstance(data, dict) and "data" in data and "content" in data["data"]:
            return data["data"]["content"]  # Extract only the "content" section
        else:
            print("Error: 'content' key not found inside 'data'.")
            return []

    except requests.exceptions.JSONDecodeError:
        print("Error: Unable to parse API response as JSON.")
        return []

def update_database(data):
    """Insert or update segment data in the database."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS content (
                        id TEXT PRIMARY KEY, 
                        tenantId TEXT, 
                        version TEXT, 
                        encrypted BOOLEAN, 
                        instanceName TEXT, 
                        segment_name TEXT
                     )''')

    cursor.execute("DELETE FROM content")

    for item in data:
        segment_name = item.get("segment", {}).get("name", "Unknown")

        cursor.execute("INSERT OR REPLACE INTO content VALUES (?, ?, ?, ?, ?, ?)",
                       (item.get("id", "Unknown"),
                        item.get("tenantId", "Unknown"),
                        item.get("version", "Unknown"),
                        item.get("encrypted", False),
                        item.get("instanceName", "Unknown"),
                        segment_name))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    segment_data = fetch_segments()
    update_database(segment_data)
