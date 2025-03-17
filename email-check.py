import imaplib
import email
import time
import sqlite3
import re
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

# Email Configuration
IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# API Configuration
API_URL = os.getenv("API_URL") + "/v1/client-configs"
API_HEADERS = {
    "x-nile-api-key": os.getenv("X_NILE_API_KEY"),
    "Content-Type": "application/json"
}

def connect_to_imap():
    """Connect to the IMAP server and login."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        return mail
    except Exception as e:
        print(f"Error connecting to IMAP: {e}")
        return None

def get_unread_emails(mail):
    """Fetch unread emails from the inbox."""
    try:
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        return messages[0].split()
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def parse_email_body(raw_email):
    """Extract MAC address and segment name from email body."""
    try:
        msg = email.message_from_bytes(raw_email)
        email_from = msg["From"]
        email_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode()
                    break
        else:
            email_body = msg.get_payload(decode=True).decode()

        match = re.search(r"Approve device ([0-9A-Fa-f:]+) to segment ([\w\s-]+)", email_body)
        if match:
            return match.group(1), match.group(2), email_from
        return None, None, None
    except Exception as e:
        print(f"Error parsing email: {e}")
        return None, None, None

def get_client_id(macaddr):
    """Fetch the client ID from the clientConfig table using the MAC address."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM clientConfig WHERE macAddress = ?", (macaddr,))
    result = cursor.fetchone()

    conn.close()

    if result:
        print(f"Found client ID {result[0]} for MAC address {macaddr}.")
        return result[0]
    else:
        print(f"Error: No client found for MAC address {macaddr}.")
        return None

def get_segment_id(segment_name):
    segment_name = segment_name.strip()
    """Fetch the segment ID from the content table using the segment name."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM content WHERE segment_name = ?", (segment_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        print(f"Found segment ID {result[0]} for segment name '{segment_name}'.")
        return result[0]
    else:
        print(f"Error: No segment found for name '{segment_name}'.")
        return None

def send_api_request(client_id, macaddr, segment_id, email_user):
    """Send REST API PATCH request to approve the device."""
    payload = {
        "macsList": [
            {
                "id": client_id,
                "macAddress": macaddr,
                "segmentId": segment_id,
                "state": "AUTH_OK",
                "description": f"Approved by {email_user}"
            }
        ]
    }

    try:
        response = requests.patch(API_URL, headers=API_HEADERS, json=payload)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 204:
            print(f"Success: Device {macaddr} assigned to segment {segment_id}. (No Content Response)")
        else:
            print(f"Success: Device {macaddr} assigned to segment {segment_id}. Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to send request - {e}")

def process_email_approvals():
    """Check for email approvals, look up details, and approve devices."""
    mail = connect_to_imap()
    if not mail:
        return

    unread_emails = get_unread_emails(mail)
    if not unread_emails:
        print("No new approval emails found.")
        return

    for email_id in unread_emails:
        _, raw_email = mail.fetch(email_id, "(RFC822)")
        mac_address, segment_name, email_user = parse_email_body(raw_email[0][1])

        if mac_address and segment_name:
            print(f"Processing approval request: MAC={mac_address}, Segment={segment_name}, User={email_user}")
            
            client_id = get_client_id(mac_address)
            segment_id = get_segment_id(segment_name)

            if client_id and segment_id:
                send_api_request(client_id, mac_address, segment_id, email_user)
            else:
                print(f"Skipping approval for {mac_address} - Missing client or segment ID.")

    mail.logout()

if __name__ == "__main__":
    while True:
        print("Checking for new approval emails...")
        process_email_approvals()
        time.sleep(60)  # Wait 60 seconds before checking again
