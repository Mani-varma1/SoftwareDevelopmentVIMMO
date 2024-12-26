from vimmo.logger.logging_config import logger
import sqlite3
from sqlite3 import Connection
from typing import Optional, List, Tuple, Dict, Any
import importlib.resources
import os




class Database:
    def __init__(self, db_path: str = 'db/panels_data.db'):
        self.db_path = db_path
        self.conn: Optional[Connection] = None

    def get_db_path(self) -> str:
        """
        Get the database path, handling both development and installed scenarios.
        """
        try:
            # First try to get the database from the installed package
            logger.info("Attempting to get the database in the installed package")
            with importlib.resources.path('vimmo.db', 'panels_data.db') as db_path:
                logger.info("Database is in the installed package: %s", db_path)
                return str(db_path)
        except Exception:
            logger.warning("failed to get the database in the installed package")

            # If that fails, try the development path
            logger.info("Attempting to get the database in the development path")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dev_db_path = os.path.join(current_dir, self.db_path)
            
            if os.path.exists(dev_db_path):
                logger.info("Database is in the development path at %s", dev_db_path)
                return dev_db_path
            else:
                logger.error("FileNotFoundError - database file could not be located in either the package or development path")
                raise FileNotFoundError("database file could not be located")
            


    def connect(self):
        """Establish a connection to the SQLite database."""
        if not self.conn:
            db_path = self.get_db_path()
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row


        
    def get_patient_data(self, patient_id: str) -> List[Tuple]:
        """Retrieve patient data by patient_id."""
        cursor = self.conn.cursor()
        query = '''
        SELECT patient_data.patient_id, patient_data.panel_id, patient_data.rcode, patient_data.panel_version,
               panel.rcodes, panel.Version
        FROM patient_data
        JOIN panel ON patient_data.panel_id = panel.Panel_ID
        WHERE patient_data.patient_id = ?
        '''
        result = cursor.execute(query, (patient_id,)).fetchall()
        return [dict(row) for row in result]  # Convert rows to dictionaries for easy JSON conversion
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
        