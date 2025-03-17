import requests
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

API_URL = os.getenv("API_URL") + "/v1/floors"
HEADERS = {"x-nile-api-key": os.getenv("X_NILE_API_KEY")}

def fetch_floors():
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_database(data):
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS floors (
                        id TEXT PRIMARY KEY, tenantId TEXT, buildingId TEXT, siteId TEXT, 
                        name TEXT, number INTEGER, description TEXT)''')

    cursor.execute("DELETE FROM floors")

    for item in data["content"]:
        cursor.execute("INSERT OR REPLACE INTO floors VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (item["id"], item["tenantId"], item["buildingId"], item["siteId"],
                        item["name"], item.get("number", 0), item.get("description", "Unknown")))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    floor_data = fetch_floors()
    update_database(floor_data)
