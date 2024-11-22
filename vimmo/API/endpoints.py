from flask_restx import Resource
from vimmo.API import api, get_db
from vimmo.utils.panelapp import PanelAppClient
from vimmo.utils.parser import IDParser, PatientParser
from vimmo.utils.arg_validator import validate_panel_id_or_Rcode_or_hgnc
from vimmo.db.db import PanelQuery

# Initialize PanelAppClient to handle external panel-related requests
panel_app_client = PanelAppClient()

# Create a namespace for panel-related endpoints
panels_space = api.namespace('panels', description='Return panel data provided by the user')

# Create a parser for handling request arguments
id_parser = IDParser.create_parser()

# Define the Panel Search endpoint
@panels_space.route('/')
class PanelSearch(Resource):
    # Document the API using the argument parser
    @api.doc(parser=id_parser)
    def get(self):
        # Parse arguments from the request
        args = id_parser.parse_args()

        # Apply custom validation for the parsed arguments
        try:
            validate_panel_id_or_Rcode_or_hgnc(args)  # Ensure only one valid parameter is provided
        except ValueError as e:
            # Return an error response if validation fails
            return {"error": str(e)}, 400

        # Retrieve the database connection
        db = get_db()
        # Initialize a query object with the database connection
        query = PanelQuery(db.conn)

        # Handle requests based on the provided argument
        if args.get("Panel_ID"):
            # Fetch panel data by Panel_ID with optional similar matches
            panel_data = query.get_panel_data(panel_id=args.get("Panel_ID"), matches=args.get("Similar_Matches"))
            return panel_data

        elif args.get("Rcode"):
            # Fetch panel data by Rcode with optional similar matches
            panel_data = query.get_panels_by_rcode(rcode=args.get("Rcode"), matches=args.get("Similar_Matches"))
            return panel_data

        elif args.get("HGNC_ID"):
            # Fetch panels associated with a specific HGNC_ID with optional similar matches
            panels_returned = query.get_panels_from_gene(hgnc_id=args.get("HGNC_ID"), matches=args.get("Similar_Matches"))
            return panels_returned

        # If no valid parameter is provided, return an error response
        return {"error": "No valid Panel_ID, Rcode, or HGNC_ID provided."}, 400


        


    


patient_space = api.namespace('patient', description='Return a patient panel provided by the user')
patient_parser = PatientParser.create_parser()
@patient_space.route("/")
class PatientClass(Resource):
    @api.doc(parser=patient_parser)
    def get(self):
                # Collect Arguements
        args = patient_parser.parse_args()

        gene_list = panel_app_client.get_genes(rcode)
        return {
            f"Paitned ID: {args['Patient_ID ']} List of genes in {rcode}" : gene_list
        }
    
