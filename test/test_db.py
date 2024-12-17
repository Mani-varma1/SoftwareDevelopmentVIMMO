import unittest
import sqlite3
from unittest.mock import MagicMock
from vimmo.db.db import Database, Query, Update


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.db = Database(":memory:")
        self.db.connect()
        self.db._initialize_tables()

    def tearDown(self):
        # Close the database connection after each test
        self.db.close()

    def test_database_connection(self):
        self.assertIsNotNone(self.db.conn, "Database connection should not be None")

    def test_get_patient_data(self):
        # Insert mock data into the database
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO panel (Panel_ID, rcodes, Version) VALUES (1, 'R208', '2.0')")
        cursor.execute(
            "INSERT INTO patient_data (Patient_ID, Rcode, Panel_ID, Date, Version) VALUES ('12345', 'R208', 1, '2024-12-14', '2.0')"
        )
        self.db.conn.commit()

        # Test the get_patient_data method
        result = self.db.get_patient_data("12345")
        self.assertEqual(len(result), 1, "Should return one patient record")
        self.assertEqual(result[0]["Rcode"], "R208", "Rcode should match the inserted data")


class TestQuery(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database and initialize tables
        self.db = Database(":memory:")
        self.db.connect()
        self.db._initialize_tables()
        self.query = Query(self.db.conn)

    def tearDown(self):
        self.db.close()

    def test_get_panel_data(self):
        # Insert mock panel data
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO panel (Panel_ID, rcodes, Version) VALUES (1, 'R208', '2.0')")
        self.db.conn.commit()

        # Test the method
        result = self.query.get_panel_data(1)
        self.assertEqual(result["Panel_ID"], 1, "Panel ID should match the query")
        self.assertEqual(result["Version"], "2.0", "Version should match the inserted data")

    def test_compare_panel_versions(self):
        # Create mock data for comparison
        historic_version = {"Gene1": "High", "Gene2": "Moderate"}
        current_version = {"Gene1": "Moderate", "Gene3": "High"}

        # Call the method
        comparison = self.query.compare_panel_versions(historic_version, current_version)
        self.assertIn("added", comparison, "Comparison should contain added genes")
        self.assertIn("removed", comparison, "Comparison should contain removed genes")
        self.assertIn("updated", comparison, "Comparison should contain updated genes")
        self.assertEqual(comparison["added"], {"Gene3": "High"}, "Gene3 should be listed as added")
        self.assertEqual(comparison["removed"], {"Gene2": "Moderate"}, "Gene2 should be listed as removed")
        self.assertEqual(comparison["updated"], {"Gene1": {"old": "High", "new": "Moderate"}},
                         "Gene1 should be updated")


class TestUpdate(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database and initialize tables
        self.db = Database(":memory:")
        self.db.connect()
        self.db._initialize_tables()
        self.update = Update(self.db.conn)

    def tearDown(self):
        self.db.close()

    def test_add_record(self):
        # Test adding a new patient record
        self.update.add_record("12345", "R208", "2024-12-14", "2.0")

        # Verify the record was added
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM patient_data WHERE Patient_ID = '12345'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "Record should be added to the database")
        self.assertEqual(result["Rcode"], "R208", "Rcode should match the added data")

    def test_add_duplicate_record(self):
        # Add a record and attempt to add the same record again
        self.update.add_record("12345", "R208", "2024-12-14", "2.0")
        self.update.add_record("12345", "R208", "2024-12-14", "2.0")  # Duplicate record

        # Verify only one record exists
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM patient_data WHERE Patient_ID = '12345'")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1, "Duplicate records should not be allowed")


if __name__ == "__main__":
    unittest.main()
