import requests
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

API_URL = os.getenv("API_URL") + "/v3/client-configs/tenant/" + os.getenv("TENANT_ID") + "?action=AUTH_WAITING_FOR_APPROVAL"
HEADERS = {"x-nile-api-key": os.getenv("X_NILE_API_KEY"), "Content-Type": "application/json"}

def fetch_clients():
    """Fetch client data from the API."""
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    
    try:
        data = response.json()
        
        # Ensure response is a list
        if isinstance(data, list):
            return data
        else:
            print("Error: API response is not a list as expected.")
            return []
    except Exception as e:
        print(f"Error parsing API response: {e}")
        return []

def update_database(data):
    """Insert or update client data in the database."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientConfig (
                        id TEXT PRIMARY KEY, 
                        macAddress TEXT, 
                        tenantId TEXT, 
                        segmentId TEXT, 
                        siteId TEXT, 
                        buildingId TEXT, 
                        floorId TEXT, 
                        state TEXT,
                        serialNo TEXT,
                        deviceId TEXT,
                        port TEXT,
                        lastSerialNo TEXT,
                        lastDeviceId TEXT,
                        lastPort TEXT,
                        mitigation BOOLEAN,
                        ruleType TEXT,
                        timestamp TEXT,
                        authenticatedBy TEXT
                     )''')

    # Extract client IDs from new data
    received_ids = {item["clientConfig"]["id"] for item in data}
    
    # Fetch existing client IDs from the database
    cursor.execute("SELECT id FROM clientConfig")
    existing_ids = {row[0] for row in cursor.fetchall()}
    
    # Identify clients to delete (those not in new data)
    to_delete = existing_ids - received_ids
    if to_delete:
        cursor.executemany("DELETE FROM clientConfig WHERE id = ?", [(id,) for id in to_delete])

    # Insert or update new clients
    for item in data:
        client = item.get("clientConfig", {})

        cursor.execute('''INSERT OR REPLACE INTO clientConfig 
                          (id, macAddress, tenantId, segmentId, siteId, buildingId, floorId, state, 
                           serialNo, deviceId, port, lastSerialNo, lastDeviceId, lastPort, 
                           mitigation, ruleType, timestamp, authenticatedBy) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (client.get("id", "Unknown"),
                        client.get("macAddress", "Unknown"),
                        client.get("tenantId", "Unknown"),
                        client.get("segmentId", "Unknown"),
                        client.get("siteId", "Unknown"),
                        client.get("buildingId", "Unknown"),
                        client.get("floorId", "Unknown"),
                        client.get("state", "Unknown"),
                        client.get("serialNo", "Unknown"),
                        client.get("deviceId", "Unknown"),
                        client.get("port", "Unknown"),
                        client.get("lastSerialNo", "Unknown"),
                        client.get("lastDeviceId", "Unknown"),
                        client.get("lastPort", "Unknown"),
                        client.get("mitigation", False),
                        client.get("ruleType", "Unknown"),
                        client.get("timestamp", "Unknown"),
                        client.get("authenticatedBy", "Unknown")))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    client_data = fetch_clients()
    update_database(client_data)
