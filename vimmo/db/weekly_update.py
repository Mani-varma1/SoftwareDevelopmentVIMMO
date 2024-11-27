import requests
import logging
from db import Database


def fetch_latest_versions(api_url):
    """
    Fetches the latest panel versions from a paginated API.

    Args:
        api_url (str): The initial URL of the API to fetch panel versions.

    Returns:
        dict: A dictionary where the keys are panel IDs and the values are their latest versions.
    """
    latest_versions = {}

    while api_url:
        try:
            # Send GET request to the API
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for HTTP issues
            data = response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from API: {e}")
            break

        # Process results in the current page
        results = data.get("results", [])
        for item in results:
            try:
                panel_id = item.get("id")
                version = float(item.get("version"))  # Convert version to a float for comparison with current version
                latest_versions[panel_id] = version
            except ValueError as e:
                logging.warning(f"Skipping invalid version for panel {item.get('id')}: {e}")

        # Move to the next page if available
        api_url = data.get("next")

    logging.info(f"Fetched {len(latest_versions)} panel versions.")
    return latest_versions


def update_or_insert_panel_versions(cursor, latest_versions):
    """
    Updates or inserts panel versions in the database.

    Args:
        cursor: SQLite database cursor for executing queries.
        latest_versions (dict): Dictionary of panel IDs and their latest versions.

    Returns:
        bool: True if any updates or inserts were made, False otherwise.
    """
    updates = False

    for panel_id, latest_version in latest_versions.items():
        # Check if the panel already exists in the database
        cursor.execute('SELECT Panel_ID, Version FROM panel WHERE Panel_ID = ?', (panel_id,))
        existing_row = cursor.fetchone()

        if existing_row:
            existing_id, existing_version = existing_row
            # Update version if it differs
            if existing_version != latest_version:
                cursor.execute(
                    'UPDATE panel SET Version = ? WHERE Panel_ID = ?',
                    (latest_version, panel_id)
                )
                logging.info(f"Updated panel {panel_id} from version {existing_version} to version {latest_version}.")
                updates = True
        else:
            # Insert new panel if it doesn't exist
            cursor.execute(
                'INSERT INTO panel (Panel_ID, Version) VALUES (?, ?)',
                (panel_id, latest_version)
            )
            logging.info(f"Inserted panel {panel_id} with version {latest_version}.")
            updates = True

    if not updates:
        logging.info("0 updates made.")
    return updates


def main():
    """
    Main function to coordinate fetching panel versions and updating the database.
    """
    # Configure logging to log to both file and console
    logging.basicConfig(
        filename='panel_updates.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler for logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    logging.info("Starting the panel update process.")

    # URL for the API endpoint
    api_url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/signedoff/?display=latest&page=1"

    # Initialize and connect to the database
    db = Database()
    db.connect()

    # Fetch latest versions from the API
    latest_versions = fetch_latest_versions(api_url)

    # Get a cursor for database operations
    cursor = db.conn.cursor()

    # Update or insert panel versions
    updates_made = update_or_insert_panel_versions(cursor, latest_versions)

    # Check for panels in the database that are missing in the latest versions
    cursor.execute('SELECT Panel_ID FROM panel')
    table_ids = {row[0] for row in cursor.fetchall()}

    missing_ids = table_ids - set(latest_versions.keys())
    if missing_ids:
        logging.info(f"IDs in the table but not in the dictionary: {missing_ids}")
    else:
        logging.info("No IDs are missing from the dictionary.")

    # Commit changes and close the database connection
    db.conn.commit()
    db.close()

    logging.info("Completed the panel update process.\n")


if __name__ == "__main__":
    main()