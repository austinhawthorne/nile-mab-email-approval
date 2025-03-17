#!/bin/bash

# Check if script is running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root (use sudo ./instll-mab-approval.sh)"
   exit 1
fi

# Define variables
INSTALL_DIR="/opt/mab-approval"
SYSTEMD_DIR="/etc/systemd/system"
ENV_FILE="$INSTALL_DIR/.env"

echo "Starting MAB Approval installation..."

# Ensure the install directory exists
echo "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

# --- Check and Install Required Dependencies ---
echo "Checking dependencies..."

# Check if Python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Installing Python3..."
    sudo apt update && sudo apt install -y python3 python3-pip
else
    echo "Python3 is already installed."
fi

# Install required Python modules
echo "Installing required Python modules..."
sudo apt install python3-dotenv python3-requests

# Check if SQLite3 is installed
if ! command -v sqlite3 &>/dev/null; then
    echo "Installing SQLite3..."
    sudo apt install -y sqlite3
else
    echo "SQLite3 is already installed."
fi

# Check if Systemd is installed
if ! systemctl --version &>/dev/null; then
    echo "Installing Systemd..."
    sudo apt install -y systemd
else
    echo "Systemd is already installed."
fi

# --- Prompt User for Environment Variables ---
echo "Configuring environment variables for .env file..."
read -p "Enter API Base URL (e.g., https://api.example.com/api): " API_URL
read -p "Enter Nile API Key: " X_NILE_API_KEY
read -p "Enter Tenant ID: " TENANT_ID
read -p "Enter SMTP Server (for sending emails): " SMTP_SERVER
read -p "Enter IMAP Server (for checking emails): " IMAP_SERVER
read -p "Enter Email Sender Address: " EMAIL_SENDER
read -p "Enter Email Password: " EMAIL_PASSWORD
read -p "Enter Email Recipient (for notifications): " EMAIL_RECIPIENT
read -p "Enter Email Account (used for checking email replies): " EMAIL_ACCOUNT

# Create .env file
echo "Writing environment variables to $ENV_FILE..."
sudo cat <<EOL > "$ENV_FILE"
# MAB Approval Configuration
API_URL="$API_URL"
X_NILE_API_KEY="$X_NILE_API_KEY"
TENANT_ID="$TENANT_ID"

# Email Configuration
SMTP_SERVER="$SMTP_SERVER"
IMAP_SERVER="$IMAP_SERVER"
EMAIL_SENDER="$EMAIL_SENDER"
EMAIL_PASSWORD="$EMAIL_PASSWORD"
EMAIL_RECIPIENT="$EMAIL_RECIPIENT"
EMAIL_ACCOUNT="$EMAIL_ACCOUNT"
EOL

# --- Copy Scripts to Installation Directory ---
echo "Copying scripts to $INSTALL_DIR"
sudo cp get-segments.py get-sites.py get-buildings.py get-floors.py get-clients.py email-check.py email-notify.py reset-test.py run-client-tasks.sh run-daily-tasks.sh /opt/mab-approval/

# Copy systemd service and timer files
echo "Copying systemd services and timers..."
sudo cp mab-approval-daily.service "$SYSTEMD_DIR/"
sudo cp mab-approval-daily.timer "$SYSTEMD_DIR/"
sudo cp mab-approval-client.service "$SYSTEMD_DIR/"
sudo cp mab-approval-client.timer "$SYSTEMD_DIR/"
sudo cp mab-approval.service "$SYSTEMD_DIR/"

# --- Set Permissions ---
echo "Setting file permissions..."
sudo chmod +x /opt/mab-approval/*.py
sudo chmod +x /opt/mab-approval/*.sh

# Secure .env file
echo "Securing .env file..."
sudo chmod 600 "$ENV_FILE"

# --- Initialize Database ---
echo "Initializing database..."
cd "$INSTALL_DIR"
/usr/bin/python3 get-sites.py
/usr/bin/python3 get-buildings.py
/usr/bin/python3 get-floors.py
/usr/bin/python3 get-segments.py
echo "Database initialization complete!"

# --- Reload Systemd and Enable Timers ---
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling and starting systemd timers..."
sudo systemctl enable --now mab-approval-daily.timer
sudo systemctl enable --now mab-approval-client.timer
sudo systemctl enable --now mab-approval

echo "Installation complete! MAB Approval system is now running."
echo "Your environment settings are saved in $ENV_FILE"
