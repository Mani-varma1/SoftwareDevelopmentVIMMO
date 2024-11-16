
from flask_restx import Resource, reqparse
from APIapp import api,get_db
from utils.panelapp import  PanelAppClient
from db.db import PanelQuery
import requests

panel_app_client = PanelAppClient()
# Create a RequestParser object to identify specific content-type requests in HTTP URLs
# The requestparser allows us to specify arguements passed via a URL, in this case, ....?content-type=application/json
parser1 = reqparse.RequestParser()
parser1.add_argument('ID',
                    type=str,
                    help='Type in Panel-ID or R code')




parser2 = reqparse.RequestParser()
parser2.add_argument('-f',
                    type=str,
                    help='Type in Patient ID or R code')
parser2 = reqparse.RequestParser()
parser2.add_argument('R code ',
                    type=str,
                    help='Type in R code')



panels_space = api.namespace('panels', description='Return panel data provided by the user')
@panels_space.route("/panels")
class NameClass(Resource):
    @api.doc(parser=parser1)
    def get(self):
        # Parse arguments
        args = parser1.parse_args()
        ID = args['ID']
        db = get_db()
        query = PanelQuery(db.conn)  # Pass the database connection to PanelQuery
        
        # Determine if input is a Panel_ID (numeric string) or an rcode (contains "R")
        if "R" in ID:
            # Treat as rcode
            panel_data = query.get_panel_data(rcode=ID)
        else:
            # Treat as Panel_ID (since it's purely numeric)
            panel_data = query.get_panel_data(panel_id=ID)
        
        # Return result as JSON
        return {
            "Panel ID or R-code": ID,
            "Associated Gene Records": panel_data
        }


    


patient_space = api.namespace('patient', description='Return a patient panel provided by the user')
@patient_space.route("/patient")
class PatientClass(Resource):
    @api.doc(parser=parser2)
    def get(self):
                # Collect Arguements
        args = parser2.parse_args()


        gene_list = panel_app_client.get_genes(rcode)
        return {
            f"Paitned ID: {args['Patient_ID ']} List of genes in {rcode}" : gene_list
        }