import requests
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

API_URL = os.getenv("API_URL") + "/v1/sites"
HEADERS = {"x-nile-api-key": os.getenv("X_NILE_API_KEY")}

def fetch_sites():
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_database(data):
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS locations (
                        id TEXT PRIMARY KEY, tenantId TEXT, name TEXT, description TEXT)''')

    cursor.execute("DELETE FROM locations")

    for item in data["content"]:
        cursor.execute("INSERT OR REPLACE INTO locations VALUES (?, ?, ?, ?)",
                       (item["id"], item["tenantId"], item["name"], item.get("description", "Unknown")))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    site_data = fetch_sites()
    update_database(site_data)
