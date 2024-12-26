from vimmo.utils.panelapp import PanelAppClient
from vimmo.db.db_query import Query
from datetime import date

class Update:
    def __init__(self, connection, test_mode=False):
        self.conn = connection
        self.query = Query(self.conn)
        self.papp = PanelAppClient(base_url="https://panelapp.genomicsengland.co.uk/api/v1/panels")
        self.test_mode = test_mode
    
    def check_presence(self, patient_id: str, rcode: str):

        current_version = str(self.query.get_db_latest_version(rcode)) # Retrieve the latest panel version from our db

        cursor = self.conn.cursor()
        does_exists = cursor.execute(f"""
        SELECT Version
        FROM patient_data
        WHERE Patient_ID = ? AND Rcode = ? AND Version = ?
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
        
        # Only commit if not in test mode
        if not self.test_mode:
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