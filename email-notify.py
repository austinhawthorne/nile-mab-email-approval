import smtplib
import sqlite3
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/opt/mab-approval/.env")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

def ensure_tables_exist():
    """Ensure the processed_clients table exists."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_clients (
                        id TEXT PRIMARY KEY)''')

    conn.commit()
    conn.close()

def fetch_new_clients():
    """Fetch new clients from clientConfig table with location details."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    # Ensure tracking table exists
    ensure_tables_exist()

    cursor.execute("""
        SELECT c.id, c.macAddress, s.name AS site, b.name AS building, f.name AS floor,
               c.serialNo, c.port
        FROM clientConfig c
        LEFT JOIN locations s ON c.siteId = s.id
        LEFT JOIN buildings b ON c.buildingId = b.id
        LEFT JOIN floors f ON c.floorId = f.id
        WHERE c.id NOT IN (SELECT id FROM processed_clients)
    """)
    
    new_clients = cursor.fetchall()

    # Mark fetched clients as processed
    for client in new_clients:
        cursor.execute("INSERT INTO processed_clients (id) VALUES (?)", (client[0],))

    conn.commit()
    conn.close()
    return new_clients

def fetch_available_segments():
    """Fetch available segments from content table."""
    conn = sqlite3.connect("/opt/mab-approval/mab_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT segment_name FROM content")
    segments = [row[0] for row in cursor.fetchall()]

    conn.close()
    return segments

def send_email(new_clients, segments):
    """Send an email notification about new devices needing segmentation."""
    if not new_clients:
        print("No new clients detected.")
        return

    subject = "New Devices Detected in Network"
    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = EMAIL_RECIPIENT
    message["Subject"] = subject

    # Format client list with full details
    client_info = "\n".join([
        f"MAC: {client[1]}, Site: {client[2] or 'Unknown'}, Building: {client[3] or 'Unknown'}, "
        f"Floor: {client[4] or 'Unknown'}, Switch: {client[5] or 'Unknown'}, Port: {client[6] or 'Unknown'}"
        for client in new_clients
    ])

    # Format segment list
    segment_options = "\n".join([f"- {seg}" for seg in segments])

    body = f"""
Hello,

The following new devices have been detected in the network:

{client_info}

Available Segments:
{segment_options}

To approve a device, reply with:
`Approve device <MAC> to segment <segment_name>`

Example:
`Approve device AA:BB:CC:DD:EE:FF to segment Acme-Devices`

Thank you.
"""

    message.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, 587) as server:
            server.starttls(context=context)
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    new_clients = fetch_new_clients()
    available_segments = fetch_available_segments()
    send_email(new_clients, available_segments)
