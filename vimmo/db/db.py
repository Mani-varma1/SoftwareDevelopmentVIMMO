
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
            with importlib.resources.path('vimmo.db', 'panels_data.db') as db_path:
                return str(db_path)
        except Exception:
            # If that fails, try the development path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dev_db_path = os.path.join(current_dir, self.db_path)
            
            if os.path.exists(dev_db_path):
                return dev_db_path
            else:
                raise FileNotFoundError("database file could not be located")
            


    def connect(self):
        """Establish a connection to the SQLite database."""
        if not self.conn:
            db_path = self.get_db_path()
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
    
    def _initialize_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create panel table (assuming it’s done elsewhere, but included here if needed)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS panel (
            Panel_ID INTEGER PRIMARY KEY,
            rcodes TEXT,
            Version TEXT
        )
        ''')
        
        # Create genes_info table (assuming it’s done elsewhere, but included here if needed)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS genes_info (
            HGNC_ID TEXT PRIMARY KEY,
            Gene_ID TEXT,
            HGNC_symbol TEXT,
            Gene_Symbol TEXT,
            GRCh38_Chr TEXT,
            GRCh38_start INTEGER,
            GRCh38_stop INTEGER,
            GRCh37_Chr TEXT,
            GRCh37_start INTEGER,
            GRCh37_stop INTEGER
        )
        ''')
        
        # Create patient_data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            panel_id INTEGER,
            rcode TEXT,
            panel_version TEXT,
            FOREIGN KEY (panel_id) REFERENCES panel (Panel_ID)
        )
        ''')

        self.conn.commit()

    def add_patient(self, patient_id: str, panel_id: Optional[int] = None, rcode: Optional[str] = None):
        """Add a new patient record using either a panel_id or an rcode."""
        cursor = self.conn.cursor()
        if panel_id:
            panel_data = cursor.execute('''
            SELECT Panel_ID, Version, rcodes
            FROM panel
            WHERE Panel_ID = ?
            ''', (panel_id,)).fetchone()
            
            if panel_data:
                version, rcodes = panel_data["Version"], panel_data["rcodes"]
                cursor.execute('''
                INSERT INTO patient_data (patient_id, panel_id, rcode, panel_version)
                VALUES (?, ?, ?, ?)
                ''', (patient_id, panel_id, rcodes, version))
        
        elif rcode:
            rcode_query = f"%{rcode}%"
            panel_data = cursor.execute('''
            SELECT Panel_ID, Version, rcodes
            FROM panel
            WHERE rcodes LIKE ?
            ''', (rcode_query,)).fetchone()
            
            if panel_data:
                panel_id, version, rcodes = panel_data["Panel_ID"], panel_data["Version"], panel_data["rcodes"]
                cursor.execute('''
                INSERT INTO patient_data (patient_id, panel_id, rcode, panel_version)
                VALUES (?, ?, ?, ?)
                ''', (patient_id, panel_id, rcodes, version))
        else:
            print("Either panel_id or rcode must be provided.")
            return None
        
        self.conn.commit()

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



# class PanelQuery:
#     def __init__(self, connection):
#         self.conn = connection

#     def get_panel_data(self, ID: Optional[str] = None, matches: bool=False):
#         """Retrieve all records associated with a specific Panel_ID or rcode."""
#         cursor = self.conn.cursor()
#         operator = "LIKE" if matches else "="
        
#         if "R" not in ID:
#             query = f'''
#             SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID, 
#                    genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr, 
#                    genes_info.GRCh38_start, genes_info.GRCh38_stop
#             FROM panel
#             JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
#             JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
#             WHERE panel.Panel_ID {operator} ?
#             '''
#             result = cursor.execute(query, (ID,)).fetchall()
        
#         else:
#             rcode_query = f"%{ID}%" if matches else ID
#             query = f'''
#             SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID, 
#                    genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr, 
#                    genes_info.GRCh38_start, genes_info.GRCh38_stop
#             FROM panel
#             JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
#             JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
#             WHERE panel.rcodes {operator} ?
#             '''
#             result = cursor.execute(query, (rcode_query,)).fetchall()

#         if result:
#             return {
#                 "ID": ID,
#                 "Associated Gene Records": [dict(row) for row in result]
#             }
#         else:
#             return {
#                 "ID": ID,
#                 "Could not find any match the ID": ID
#             }
                

#     def get_panels_from_gene(self, hgnc_id: str, matches: bool=False) -> list[
#         dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes]]:
#         cursor = self.conn.cursor()
#         operator = "LIKE" if matches else "="
#         query = f'''
#         SELECT panel.Panel_ID, panel.rcodes, genes_info.Gene_Symbol
#         FROM panel
#         Join panel_genes on panel.Panel_ID = panel_genes.Panel_ID
#         join genes_info on panel_genes.HGNC_ID = genes_info.HGNC_ID
#         WHERE panel_genes.HGNC_ID {operator} ?
#         '''

#         result = cursor.execute(query, (hgnc_id,)).fetchall()
#         if result:
#             return{
#                 "HGNC ID": hgnc_id,
#                 "Panels": [dict(row) for row in result]
#                 }
#         else:
#             return {
#                 "ID": hgnc_id,
#                 "Could not find any match the HGNC ID": hgnc_id
#             }
        
class PanelQuery:
    def __init__(self, connection):
        self.conn = connection

    def get_panel_data(self, panel_id: Optional[int] = None, matches: bool=False):
        """Retrieve all records associated with a specific Panel_ID."""
        if panel_id is None:
            raise ValueError("Panel_ID must be provided.")

        cursor = self.conn.cursor()
        operator = "LIKE" if matches else "="

        # For numeric Panel_ID, LIKE is not typically used. Consider enforcing exact matches.
        if matches:
            # If 'matches' is True, you might want to convert the panel_id to a string and use LIKE
            # However, this is unusual for numeric IDs. Consider whether this is necessary.
            panel_id_query = f"%{panel_id}%"
            query = f'''
            SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID, 
                   genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr, 
                   genes_info.GRCh38_start, genes_info.GRCh38_stop
            FROM panel
            JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
            JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
            WHERE panel.Panel_ID LIKE ?
            '''
            result = cursor.execute(query, (panel_id_query,)).fetchall()
        else:
            # Exact match for Panel_ID
            query = f'''
            SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID, 
                   genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr, 
                   genes_info.GRCh38_start, genes_info.GRCh38_stop
            FROM panel
            JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
            JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
            WHERE panel.Panel_ID = ?
            '''
            result = cursor.execute(query, (panel_id,)).fetchall()

        if result:
            return {
                "Panel_ID": panel_id,
                "Associated Gene Records": [dict(row) for row in result]
            }
        else:
            return {
                "Panel_ID": panel_id,
                "Message": "No matches found."
            }

    def get_panels_by_rcode(self, rcode: str, matches: bool = False):
        """Retrieve all records associated with a specific rcode."""
        cursor = self.conn.cursor()
        operator = "LIKE" if matches else "="
        rcode_query = f"%{rcode}%" if matches else rcode

        # Query by rcode
        query = f'''
        SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID, 
               genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr, 
               genes_info.GRCh38_start, genes_info.GRCh38_stop
        FROM panel
        JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
        JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
        WHERE panel.rcodes {operator} ?
        '''
        result = cursor.execute(query, (rcode_query,)).fetchall()

        if result:
            return {
                "Rcode": rcode,
                "Associated Gene Records": [dict(row) for row in result]
            }
        else:
            return {
                "Rcode": rcode,
                "Message": "No matches found for this rcode."
            }

    def get_panels_from_gene(self, hgnc_id: str, matches: bool=False) -> list[dict]:
        cursor = self.conn.cursor()
        operator = "LIKE" if matches else "="
        query = f'''
        SELECT panel.Panel_ID, panel.rcodes, genes_info.Gene_Symbol
        FROM panel
        JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
        JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
        WHERE panel_genes.HGNC_ID {operator} ?
        '''

        result = cursor.execute(query, (hgnc_id,)).fetchall()
        if result:
            return {
                "HGNC ID": hgnc_id,
                "Panels": [dict(row) for row in result]
            }
        else:
            return {
                "HGNC ID": hgnc_id,
                "Message": "Could not find any match for the HGNC ID."
            }
