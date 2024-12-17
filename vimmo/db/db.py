
import sqlite3
from sqlite3 import Connection
from typing import Optional, List, Tuple, Dict, Any
import importlib.resources
import os
from datetime import date
from vimmo.utils.panelapp import PanelAppClient
import requests


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
            version INT,
            date DATE,
            FOREIGN KEY (panel_id) REFERENCES panel (Panel_ID)
        )
        ''')

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
        
class Query:
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
        
    def get_gene_list(self,panel_id,r_code,matches):
        if panel_id:
            panel_data = self.get_panel_data(panel_id=panel_id, matches=matches)
            if "Message" in panel_data:
                return panel_data
            gene_query={record["HGNC_ID"] for record in panel_data["Associated Gene Records"]}
        elif r_code:
            panel_data = self.get_panels_by_rcode(rcode=r_code, matches=matches)
            if "Message" in panel_data:
                return panel_data
            gene_query={record["HGNC_ID"] for record in panel_data["Associated Gene Records"]}
        return gene_query
    
    def get_gene_symbol(self, ids_to_replace):

        cursor = self.conn.cursor()
        placeholders = ', '.join(['?'] * len(ids_to_replace))
        query = f'''
            SELECT HGNC_ID, HGNC_symbol
            FROM genes_info
            WHERE HGNC_ID IN ({placeholders})
            '''
        
        result = cursor.execute(query, list(ids_to_replace)).fetchall()
        return result
    
    def local_bed(self, gene_query, genome_build):
        if genome_build=="GRCh38":
            cursor = self.conn.cursor()
            # Prepare placeholders for SQL IN clause
            placeholders = ','.join(['?'] * len(gene_query))
            query = f'''
            SELECT Chromosome, Start, End, Name, HGNC_ID, Transcript, Strand, Type
            FROM bed38
            WHERE HGNC_ID IN ({placeholders})
            '''
            local_bed_records=cursor.execute(query, list(gene_query))
            return local_bed_records
        elif genome_build=="GRCh37":
            cursor = self.conn.cursor()
            # Prepare placeholders for SQL IN clause
            placeholders = ','.join(['?'] * len(gene_query))
            query = f'''
            SELECT Chromosome, Start, End, Name, HGNC_ID, Transcript, Strand, Type
            FROM bed37
            WHERE HGNC_ID IN ({placeholders})
            '''
            local_bed_records = cursor.execute(query, list(gene_query))
            return local_bed_records
    
    def check_patient_history(self, Patient_id: str, Rcode) -> str:
            """
            Retrieves the latest test version for a given patient and R code within the Vimmo database. 
            
            Parameters
            ----------
            Patient_id: str (required)
            The patient id, linked to the test history for a given patient

            Rcode: str (required)
            A specific R code to search for a given patient
            

            Returns
            -------
            patient_history: float
            The most recent version of a R code that a given patient has had
            
            Notes
            -----
            - Excutes a simple SQL query
            - Queries the patient_data table
            - For the entire test history of a patient, see return_all_records()

            Example
            -----
            User UI input: Patient ID = 123, Rcode R208

            Query class method: check_patient_history(123, R208) -> 2.5 

            Here, '2.5' is the most recent version of R208 conducted on patient 123
            """
            
            cursor = self.conn.cursor()

            
            patient_history = cursor.execute(f'''
            SELECT Version
            FROM patient_data
            WHERE DATE = (SELECT MAX(DATE) FROM patient_data WHERE Rcode = ? AND Patient_ID = ?)         
            ''', (Rcode, Patient_id)).fetchone()
            if patient_history is None:
                return None
            else: 
                return patient_history[0]

    def get_db_latest_version(self, Rcode: str) -> str:
        """
        Returns the most uptodate panel verision stored within the Vimmo database for an input R code

        Parameters
        ----------
        Rcode : str
        The R code to search for in the Vimmo's database

        Returns
        -------
        panel_id: str
        The corresponding version for the corresponding R code panels_data.db - 'panel' table (see schema in repo)

        Notes
        -----
        - Excutes a simple SQL query that that selections the

        Example
        -----
        User UI input: R208
        Query class method: rcode_to_panelID(R208) -> 635 
        
        Here 635 is the R208 panel ID, as of (26/11/24)
        """
        cursor = self.conn.cursor()


        database_version = cursor.execute( f'''
        SELECT panel.Version
        FROM panel
        WHERE panel.rcodes = ?
        ''', (Rcode,)).fetchone()
        
        if database_version == None:
            return None
        else:
            return database_version[0]
    
    def rcode_to_panelID(self, Rcode: str) -> str:
        """
        Returns the panelapp panel ID for an input panelapp Rcode

        Parameters
        ----------
        Rcode : str
        The R code to search for in the Vimmo's database

        Returns
        -------
        panel_id[0]: str
        The corresponding panel ID for the input R code


        Notes
        -----
        - Executes a simple SQL query to Vimmo's 'panel' table (see db schema in repository root)
        - panel_id[0] indexed to access the sql lite 'row' object type

        Example
        -----
        User UI input: R208
        Query class method: rcode_to_panelID(R208) -> 635 
        
        Here 635 is the R208 panel ID, as of (26/11/24)
        """

        cursor = self.conn.cursor()

        
        panel_id = cursor.execute(f'''
        SELECT Panel_ID
        FROM panel
        WHERE rcodes = ?
        ''', (Rcode,)).fetchone()
        
        if panel_id is None:
            return None
        else:
            return panel_id[0] 
    
    def return_all_records(self, Patient_id: str) -> str:
        """
        Returns all historical tests stored for a given patient

        Parameters
        ----------
        Rcode : str
        The R code to search for in the Vimmo's database

        Returns
        -------
        patient_records: list[list[]]
        The list of Rcodes, versions and dates that a patient has had


        Notes
        -----
        - Executes a simple SQL query to Vimmo's 'patient_data' table (see db schema in repository root)
        - Returns a list of lists. Each nested list represents a row in the 

        Example
        -----
        User UI input: R208
        Query class method: return_all_records(R208) -> [[R208, 2.5, 2000-1-5],[R132, 1, 2024-1-2]] 
        
        """
        cursor = self.conn.cursor()
        
        patient_records_rows = cursor.execute(f'''
        SELECT Rcode, Version, Date
        FROM patient_data
        WHERE Patient_ID = ?
        ''', (Patient_id,)).fetchall()  # The returned query is a sqlite3 row object list[tuples()].

        patient_records = {}  # Instantiation of object for output dict.
        for record in patient_records_rows:
            patient_records.update({record["Date"]: [record["Rcode"], record["Version"]]})
        return patient_records
    
    def return_all_patients(self, Rcode: str) -> dict:       
        cursor = self.conn.cursor()
        rcode_records_rows = cursor.execute(f"""
        SELECT Patient_ID, Version, Date
        FROM patient_data
        WHERE Rcode = ?
        """, (Rcode,)).fetchall() 

        rcode_records = {} # Instantiation of object for output dict
        for record in rcode_records_rows:
            rcode_records.update({record["Date"]: [record["Patient_ID"], record["Version"]]})
        return rcode_records
    

    def current_panel_contents(self, panelID: str) -> dict:
        cursor = self.conn.cursor()
        query = f"""
        SELECT HGNC_ID, Confidence
        FROM panel_genes 
        WHERE panel_genes.Panel_ID = ?
"""
        current_panel_data = cursor.execute(query, (panelID,)).fetchall()
        current_data = {} # Instantiation of object for output dict{}
        for tuple in current_panel_data:  # Loop through the tuples (HGNC ID, Confidence)
            current_data.update({tuple["HGNC_ID"]: tuple["Confidence"]})   # Insert gene, conf pair into output dict
        return current_data
    
    


    def historic_panel_retrieval(self, panelID: str, version: float):
        """ 
        Returns panel contents for an archived panel version

        Parameters
        ----------
        PanelID: str
        The panelApp panelID for the queried R code

        version: float
        The version number of the archived panel

        Returns
        -------
        historical_data: dict{}
        The contents of the archived panel version


        Notes
        -----
        - Executes a simple SQL query to Vimmo's 'panel_genes_archive' table (see db schema in repository)
        - The dictionary returns key value pairs as follows {HGNC_ID:Confidence} 

        Example
        -----
        Input: PanelID 635, version 2.1
        Query class method: historic_panel_retrieval(635,2.1) -> {
                                                                "HGNC:1071": 3,
                                                                "HGNC:2186": 2,
                                                                "HGNC:20000": 3
                                                                }
        """
        
        cursor = self.conn.cursor()
        operator = "="

        query = f"""
        SELECT HGNC_ID, Confidence
        FROM panel_genes_archive
        WHERE panel_genes_archive.Panel_ID {operator} ? AND panel_genes_archive.Version {operator} ?
"""

        historic_panel_data = cursor.execute(query, (panelID, version)).fetchall()
        historic_data = {} # Instantiation of object for output dict{}
        for tuple in historic_panel_data:  # Loop through the tuples (HGNC ID, Confidence)
                                        
            historic_data.update({tuple["HGNC_ID"]: tuple["Confidence"]})   # Insert gene, conf pair into output dict

        return historic_data

    def compare_panel_versions(self, historic_version: dict, current_version: dict) -> dict:
        # find genes added
        genes_added = {}
        for gene in current_version.keys():
            if gene in historic_version.keys():
                pass
            else:
                genes_added.update({gene:current_version[gene]})
        # find genes remove
        genes_removed = {}
        for gene in historic_version.keys():
            if gene in current_version:
                pass
            else:
                genes_removed.update({gene:historic_version[gene]})
        # find gene conf change
        conf_changes = {}
        for HGNC in current_version.keys():
            if HGNC not in historic_version.keys(): # If gene new to panel, pass
                pass
            elif HGNC in historic_version.keys() and current_version[HGNC] == historic_version[HGNC]: # If gene confidence unchanged, pass
                pass
            
            elif HGNC in historic_version.keys() and current_version[HGNC] != historic_version[HGNC]: # If gene in both versions and has changed, up
                conf_changes.update({HGNC:(historic_version[HGNC],current_version[HGNC])})
            

        return [genes_added, genes_removed, conf_changes] # Return the panel comparison information

class Update:
    def __init__(self,connection):
        self.conn = connection
        self.query = Query(self.conn)
        self.papp = PanelAppClient(base_url="https://panelapp.genomicsengland.co.uk/api/v1/panels")
    
    def check_presence(self, patient_id: str, rcode: str):

        current_version = str(self.query.get_db_latest_version(rcode)) # Retrieve the latest panel version from our db

        cursor = self.conn.cursor()
        operator = "="
        does_exists = cursor.execute(f"""
        SELECT Version
        FROM patient_data
        WHERE Patient_ID {operator} ? AND Rcode {operator} ? AND Version {operator} ?
        """, (patient_id, rcode, current_version)).fetchone() # query patient_data table for entries matching the query rcode, patient id and current version
        
        if does_exists != None: # if a value is returned, a patient record matches the query
            return current_version # return the current version 
        else:
            return False 

    
    def add_record(self, patient_id: str, rcode: str) -> str:
        """Add a new patient record using an rcode or panel_id."""
        
        version = str(self.query.get_db_latest_version(rcode)) # Retrieve the latest panel version from our db
        panel_id = str(self.query.rcode_to_panelID(rcode))     # Retrieve the panel id for input Rcode
        date_today = str(date.today())                         # Create object with date of query
        cursor = self.conn.cursor()
        
        cursor.execute(f"""
        INSERT INTO patient_data 
        VALUES (?, ?, ?, ?, ?) 
        """, (patient_id, panel_id, rcode, version, date_today)) # Insert data into table
        
        self.conn.commit()
        return f'Check the db!'
    
    def update_panels_version(self, rcode, new_version, panel_id):
        """ Update the panel table with new version """
 
        cursor = self.conn.cursor()
        operator = "="
        cursor.execute(f"""
        UPDATE panel
        SET Panel_ID {operator} ?, rcodes {operator} ?, Version {operator} ?
        WHERE Panel_ID {operator} ? AND rcodes {operator} ?
        """, (panel_id,rcode,new_version,panel_id,rcode))

        self.conn.commit()
    
    def archive_panel_contents(self, panel_id: str, archive_version: str):
        """ Archive the contents of an outdated panel version """
        cursor = self.conn.cursor()
        cursor.execute(
                    '''
                    INSERT INTO panel_genes_archive (Panel_ID, HGNC_ID, Version, Confidence)
                    SELECT Panel_ID, HGNC_ID, ?, Confidence
                    FROM panel_genes
                    WHERE Panel_ID = ?
                    ''', (archive_version,panel_id,)

                )
        self.conn.commit()

    def update_gene_contents(self, Rcode, panel_id):
        """ Updates the panel_genes table with new panel version contents"""
        genes = self.papp.get_genes_HGNC(Rcode)

        cursor = self.conn.cursor()

        cursor.execute(f"""
        DELETE FROM panel_genes
        WHERE Panel_ID = ?
        """,(panel_id,))

        for gene in genes:
        
            cursor.execute(f"""
            INSERT INTO panel_genes (Panel_ID, HGNC_ID, Confidence)
            VALUES (?, ?, ?)
            """,(panel_id, gene, 3))
        
        self.conn.commit()
        
        return {panel_id: genes} 


    