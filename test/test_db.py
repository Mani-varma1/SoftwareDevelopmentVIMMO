import unittest
import sqlite3
from unittest.mock import MagicMock
from vimmo.db.db import Database 
from vimmo.db.db_query import Query
from vimmo.db.db_update import Update
from vimmo.db.db_downgrade import Downgrade


import unittest
import sqlite3
from vimmo.db.db import Database

class TestDatabase(unittest.TestCase):
    """
    Test suite for the Database class functionality.
    
    This test suite focuses on verifying the database operations work correctly
    while ensuring no test data persists in the actual database. It uses
    transaction rollback to maintain database integrity.

    Attributes:
        db (Database): Instance of the Database class being tested
    """

    def setUp(self):
        """
        Test fixture setup executed before each test method.
        
        This method:
        1. Creates a new database connection
        2. Starts a transaction to isolate test data
        
        Any changes made during the test will be contained within this transaction
        and rolled back in tearDown().
        """
        # Initialize database connection with actual database file
        self.db = Database()
        self.db.connect()
        
        # Start a transaction - this ensures all subsequent operations
        # can be rolled back, preventing test data from persisting
        self.db.conn.execute("BEGIN TRANSACTION")

    def tearDown(self):
        """
        Test fixture cleanup executed after each test method.
        
        This method:
        1. Rolls back any changes made during the test
        2. Closes the database connection
        
        The rollback ensures the database remains unchanged regardless
        of what operations were performed during the test.
        """
        if self.db.conn:
            # Roll back all changes made during the test
            self.db.conn.rollback()
            # Clean up by closing the connection
            self.db.close()

    def test_database_connection(self):
        """
        Test case verifying database connection is established properly.
        
        Ensures that:
        1. Connection object exists
        2. Connection is of correct type (sqlite3.Connection)
        
        Returns:
            None
        
        Raises:
            AssertionError: If connection is None or of wrong type
        """
        self.assertIsNotNone(self.db.conn, "Database connection should not be None")
        self.assertTrue(
            isinstance(self.db.conn, sqlite3.Connection),
            "Connection should be an instance of sqlite3.Connection"
        )

    def test_add_and_get_patient_data(self):
        """
        Test case for adding and retrieving patient data.
        
        This test:
        1. Adds a test panel if it doesn't exist
        2. Inserts test patient data
        3. Retrieves the data using get_patient_data
        4. Verifies the retrieved data matches what was inserted
        
        All changes are rolled back after the test completes.
        
        Returns:
            None
            
        Raises:
            AssertionError: If data retrieval doesn't match expected results
        """
        cursor = self.db.conn.cursor()
        
        # Insert a test panel record if it doesn't already exist
        # Using ID 999 to avoid conflicts with real data
        cursor.execute("""
            INSERT INTO panel (Panel_ID, rcodes, Version) 
            SELECT 01010, 'R208', '2.0'
            WHERE NOT EXISTS (
                SELECT 1 FROM panel WHERE Panel_ID = 01010
            )
        """)
        
        # Test patient ID using prefix 'TEST' to clearly identify test data
        test_patient_id = 'TEST123'
        
        # Insert test patient record
        cursor.execute("""
            INSERT INTO patient_data 
            (Patient_ID, Panel_ID, Rcode, Version, Date) 
            VALUES 
            (?, 01010, 'R208', '2.0', '2024-12-14')
        """, (test_patient_id,))
        
        # Retrieve the patient data using the method being tested
        result = self.db.get_patient_data(test_patient_id)
        
        # Verify the correct number of records was returned
        self.assertEqual(
            len(result), 
            1, 
            "Should return exactly one patient record"
        )
        
        # Verify the returned data matches what was inserted
        self.assertEqual(
            result[0]['patient_id'], 
            test_patient_id,
            "Retrieved patient ID should match inserted ID"
        )
        self.assertEqual(
            result[0]['rcode'], 
            'R208',
            "Retrieved Rcode should match inserted Rcode"
        )

    def test_get_nonexistent_patient(self):
        """
        Test case for attempting to retrieve a non-existent patient.
        
        Verifies that querying for a patient that doesn't exist returns
        an empty result set rather than raising an error.
        
        Returns:
            None
            
        Raises:
            AssertionError: If result is not an empty list
        """
        result = self.db.get_patient_data('NONEXISTENT_ID')
        self.assertEqual(
            len(result), 
            0, 
            "Query for non-existent patient should return empty list"
        )
        self.assertEqual(result[0]["Rcode"], "R208", "Rcode should match the inserted data")


# class TestQuery(unittest.TestCase):
#     def setUp(self):
#         # Create an in-memory SQLite database and initialize tables
#         self.db = Database(":memory:")
#         self.db.connect()
#         self.query = Query(self.db.conn)

#     def tearDown(self):
#         self.db.close()

#     def test_get_panel_data(self):
#         # Insert mock panel data
#         cursor = self.db.conn.cursor()
#         cursor.execute("INSERT INTO panel (Panel_ID, rcodes, Version) VALUES (1, 'R208', '2.0')")
#         self.db.conn.commit()

#         # Test the method
#         result = self.query.get_panel_data(1)
#         self.assertEqual(result["Panel_ID"], 1, "Panel ID should match the query")# this is wrong
#         self.assertEqual(result["Version"], "2.0", "Version should match the inserted data")

#     def test_compare_panel_versions(self):
#         # Create mock data for comparison
#         historic_version = {"Gene1": "High", "Gene2": "Moderate"}
#         current_version = {"Gene1": "Moderate", "Gene3": "High"}

#         # Call the method
#         comparison = self.query.compare_panel_versions(historic_version, current_version)
#         self.assertIn("added", comparison, "Comparison should contain added genes")
#         self.assertIn("removed", comparison, "Comparison should contain removed genes")
#         self.assertIn("updated", comparison, "Comparison should contain updated genes")
#         self.assertEqual(comparison["added"], {"Gene3": "High"}, "Gene3 should be listed as added")
#         self.assertEqual(comparison["removed"], {"Gene2": "Moderate"}, "Gene2 should be listed as removed")
#         self.assertEqual(comparison["updated"], {"Gene1": {"old": "High", "new": "Moderate"}},
#                          "Gene1 should be updated")


# class TestUpdate(unittest.TestCase):
#     def setUp(self):
#         # Create an in-memory SQLite database and initialize tables
#         self.db = Database(":memory:")
#         self.db.connect()
#         self.update = Update(self.db.conn)

#     def tearDown(self):
#         self.db.close()

#     def test_add_record(self):
#         # Test adding a new patient record
#         self.update.add_record("12345", "R208", "2024-12-14", "2.0")

#         # Verify the record was added
#         cursor = self.db.conn.cursor()
#         cursor.execute("SELECT * FROM patient_data WHERE Patient_ID = '12345'")
#         result = cursor.fetchone()
#         self.assertIsNotNone(result, "Record should be added to the database")
#         self.assertEqual(result["Rcode"], "R208", "Rcode should match the added data")

#     def test_add_duplicate_record(self):
#         # Add a record and attempt to add the same record again
#         self.update.add_record("12345", "R208", "2024-12-14", "2.0")
#         self.update.add_record("12345", "R208", "2024-12-14", "2.0")  # Duplicate record

#         # Verify only one record exists
#         cursor = self.db.conn.cursor()
#         cursor.execute("SELECT * FROM patient_data WHERE Patient_ID = '12345'")
#         result = cursor.fetchall()
#         self.assertEqual(len(result), 1, "Duplicate records should not be allowed")


if __name__ == "__main__":
    unittest.main()
