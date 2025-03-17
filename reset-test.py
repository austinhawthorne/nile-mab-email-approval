import sqlite3

def clear_processed_clients():
    """Delete all entries from the processed_clients table in mab_data.db."""
    conn = sqlite3.connect("mab_data.db")
    cursor = conn.cursor()

    # Check if table exists before attempting deletion
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_clients'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("DELETE FROM processed_clients")
        conn.commit()
        print("All entries in processed_clients table have been deleted.")
    else:
        print("Table processed_clients does not exist.")

    conn.close()

if __name__ == "__main__":
    clear_processed_clients()
