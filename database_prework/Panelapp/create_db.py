import csv
import sqlite3

def main():
    csv_file_name = '../createdb/latest_panel_versions.csv'  # Your existing CSV file
    db_file_name = 'panel_data.db'               # The SQLite database file to create

    # Connect to (or create) the SQLite database
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    # Create the table in the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS panels (
            Panel_ID INTEGER PRIMARY KEY,
            rcodes TEXT,
            Version TEXT
        )
    ''')

    # Read data from the CSV file and insert into the database
    with open(csv_file_name, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            panel_id = int(row['Panel_ID'])
            rcodes= row['rcodes']
            version = row['Version']

            # Insert or replace the record in the database
            cursor.execute('''
                INSERT OR REPLACE INTO panels (Panel_ID, rcodes, Version)
                VALUES (?, ?, ?)
            ''', (panel_id, rcodes, version))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print(f"SQLite database '{db_file_name}' has been created and populated from '{csv_file_name}'.")

if __name__ == '__main__':
    main()