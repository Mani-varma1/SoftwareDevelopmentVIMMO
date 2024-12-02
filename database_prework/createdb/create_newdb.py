import sqlite3
import pandas as pd

# Load the CSV files into pandas DataFrames
csv1 = 'latest_panel_versions.csv'  # Update with actual file path for CSV file 1
csv2 = 'genes.csv'  # Update with actual file path for CSV file 2


df_panel = pd.read_csv(csv1)
df_panel_genes_raw = pd.read_csv(csv2)

# Connect to SQLite database (it will create a new database file if it doesn't exist)
conn = sqlite3.connect('../../vimmo/db/panels_data.db')
cursor = conn.cursor()

# Create Table 1: panel
cursor.execute('''
CREATE TABLE IF NOT EXISTS panel (
    Panel_ID INTEGER PRIMARY KEY,
    rcodes TEXT,
    Version TEXT
)
''')

# Create Table 2: panel_genes with Panel_ID, HGNC_ID, and Confidence
cursor.execute('''
CREATE TABLE IF NOT EXISTS panel_genes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Panel_ID INTEGER,
    HGNC_ID TEXT,
    Confidence INTEGER,
    FOREIGN KEY (Panel_ID) REFERENCES panel (Panel_ID)
)
''')

# Create Table 3: genes_info to store unique gene information for each HGNC_ID
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

# Create Table 4: patient_test_history to stores previous RCODES and versions
cursor.execute('''
CREATE TABLE IF NOT EXISTS patient_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    panel_id INTEGER,
    rcode TEXT,
    panel_version TEXT,
    date DATE,
    FOREIGN KEY (panel_id) REFERENCES panel (Panel_ID)
)
''')

# Create Table 5: archive panel_genes with Panel_ID, HGNC_ID, Version and Confidence
cursor.execute('''
CREATE TABLE IF NOT EXISTS panel_genes_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Panel_ID INTEGER,
    HGNC_ID TEXT,
    Version TEXT,
    Confidence INTEGER,
    FOREIGN KEY (Panel_ID) REFERENCES panel (Panel_ID)
)
''')

# Populate Table 1: panel
df_panel.to_sql('panel', conn, if_exists='replace', index=False)

# Populate Table 3: genes_info with unique gene entries from df_panel_genes_raw
df_genes_info = df_panel_genes_raw[['HGNC ID', 'Gene ID', 'HGNC symbol', 'Gene Symbol', 'GRCh38 Chr', 
                                    'GRCh38 start', 'GRCh38 stop', 'GRCh37 Chr', 'GRCh37 start', 'GRCh37 stop']].drop_duplicates()
df_genes_info.columns = ['HGNC_ID', 'Gene_ID', 'HGNC_symbol', 'Gene_Symbol', 'GRCh38_Chr', 
                         'GRCh38_start', 'GRCh38_stop', 'GRCh37_Chr', 'GRCh37_start', 'GRCh37_stop']
df_genes_info.to_sql('genes_info', conn, if_exists='replace', index=False)

# Populate Table 2: panel_genes with Panel_ID, HGNC_ID, and Confidence from df_panel_genes_raw
df_panel_genes = df_panel_genes_raw[['Panel ID', 'HGNC ID', 'Confidence']].copy()
df_panel_genes.columns = ['Panel_ID', 'HGNC_ID', 'Confidence']
df_panel_genes.to_sql('panel_genes', conn, if_exists='replace', index=False)

# Commit the changes
conn.commit()