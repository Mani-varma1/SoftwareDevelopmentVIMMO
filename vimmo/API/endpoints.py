from flask_restx import Resource
from vimmo.API import api, get_db
from vimmo.utils.panelapp import PanelAppClient
from vimmo.utils.parser import IDParser, PatientParser
from vimmo.utils.arg_validator import validate_id_or_hgnc
from vimmo.db.db import PanelQuery

panel_app_client = PanelAppClient()

panels_space = api.namespace('panels', description='Return panel data provided by the user')
id_parser = IDParser.create_parser()

# Define Panel Endpoint
@panels_space.route('/')
class PanelSearch(Resource):
    @api.doc(parser=id_parser)
    def get(self):
        # Parse arguments
        args = id_parser.parse_args()

        # Apply custom validation
        try:
            validate_id_or_hgnc(args)
        except ValueError as e:
            return {"error": str(e)}, 400

        db = get_db()
        query = PanelQuery(db.conn)  # Pass the database connection to PanelQuery

        # Check if Panel_ID is provided
        if args.get("Panel_ID"):
            panel_data = query.get_panel_data(panel_id=args.get("Panel_ID"), matches=args.get("Similar_Matches"))
            return panel_data

        # Check if an Rcode is provided
        elif args.get("Rcode"):
            rcode = args.get("Rcode")
            panel_data = query.get_panels_by_rcode(rcode=rcode, matches=args.get("Similar_Matches"))
            return panel_data

        # Check if an HGNC_ID is provided
        elif args.get("HGNC_ID"):
            panels_returned = query.get_panels_from_gene(hgnc_id=args.get("HGNC_ID"), matches=args.get("Similar_Matches"))
            return panels_returned

        # If none of the valid parameters are provided, return an error
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
    
