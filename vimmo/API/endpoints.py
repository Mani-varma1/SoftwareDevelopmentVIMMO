
from flask import send_file
from flask_restx import Resource
from vimmo.API import api,get_db
from vimmo.utils.panelapp import  PanelAppClient
from vimmo.utils.variantvalidator import VarValClient, VarValAPIError
from vimmo.utils.parser import IDParser, PatientParser, DownloadParser, UpdateParser
from vimmo.utils.arg_validator import validate_panel_id_or_Rcode_or_hgnc
from vimmo.db.db import Query


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
            validate_panel_id_or_Rcode_or_hgnc(args,panel_space=True)  # Ensure only one valid parameter is provided
        except ValueError as e:
            # Return an error response if validation fails
            return {"error": str(e)}, 400

        # Retrieve the database connection
        db = get_db()
        # Initialize a query object with the database connection
        query = Query(db.conn)

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






download_parser=DownloadParser.create_parser()
@panels_space.route('/download')
class PanelDownload(Resource):
    @api.doc(parser=download_parser)
    def get(self):
        """
        Endpoint to download panel data as a BED file.

        Query Parameters:
        - HGNC_ID (str): Gene identifier for querying (e.g., HGNC ID or symbol).
        - genome_build (str): Genome build version (default: 'GRCh38').
        - transcript_set (str): Transcript set to use (e.g., 'refseq', 'ensembl', 'all'; default: 'all').
        - limit_transcripts (str): Specifies transcript filtering ('mane', 'select', 'all'; default: 'all').

        Returns:
        - FileResponse: A downloadable BED file containing gene data.
        """
        # Parse user-provided arguments from the request
        args = download_parser.parse_args()


        # # Apply custom validation
        try:
            validate_panel_id_or_Rcode_or_hgnc(args, bed_space=True)
        except ValueError as e:
            return {"error": str(e)}, 400

        panel_id=args.get("Panel_ID",None)
        r_code=args.get("Rcode",None)


        # Retrieve the database connection
        db = get_db()
        # Initialize a query object with the database connection
        query = Query(db.conn)

        if panel_id:
            panel_data = query.get_panel_data(panel_id=args.get("Panel_ID"), matches=args.get("Similar_Matches"))
            if "Message" in panel_data:
                return panel_data
            gene_query={record["HGNC_ID"] for record in panel_data["Associated Gene Records"]}
            gene_query="|".join(gene_query)
        elif r_code:
            panel_data = query.get_panels_by_rcode(rcode=args.get("Rcode"), matches=args.get("Similar_Matches"))
            if "Message" in panel_data:
                return panel_data
            gene_query={record["HGNC_ID"] for record in panel_data["Associated Gene Records"]}
            gene_query="|".join(gene_query)
        else:
            gene_query = args.get("HGNC_ID",None)


        genome_build = args.get('genome_build', 'GRCh38')
        transcript_set = args.get('transcript_set', 'all')
        limit_transcripts = args.get('limit_transcripts', 'mane_select')
        

        # Initialize the VariantValidator client
        var_val_client = VarValClient()

        try:
            # Generate the BED file content
            bed_file = var_val_client.parse_to_bed(
                gene_query=gene_query,
                genome_build=genome_build,
                transcript_set=transcript_set,
                limit_transcripts=limit_transcripts
            )
        except VarValAPIError as e:
            # Return an error response if processing fails
            return {"error": str(e)}, 500


        # Generate a meaningful filename for the download
        if panel_id:
            filename = f"{panel_id}_{genome_build}_{limit_transcripts}.bed"
        elif r_code:
            filename = f"{r_code}_{genome_build}_{limit_transcripts}.bed"
        else:
            filename = f"Genes_{genome_build}_{limit_transcripts}.bed"

        # Return the BED file as a downloadable response
        return send_file(
            bed_file,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )



patient_space = api.namespace('patient', description='Return a patient panel provided by the user')
patient_parser = PatientParser.create_parser()
@patient_space.route("/patient")
class PatientClass(Resource):
    @api.doc(parser=patient_parser)
    def get(self):
                # Collect Arguements
        args = patient_parser.parse_args()
        # Fetch the database and connect
        db = get_db()
        
        query = Query(db.conn)
        if args["R code"] == None:
            # Show all Tests/version for a given patient ID workflow
            # patient_query(Patient ID) -> all rows
            patient_records = query.return_all_records(args["Patient ID"])
   
            return f'patient records = {patient_records}'
            
        else:
            panel_id = query.rcode_to_panelID(args["R code"]) # Convert the rcode into the panel id (needed for signedoff panel version endpoint)
            # Version comparison workflow
            # Check database version is up to date
            
            lastest_online_version = panel_app_client.get_latest_online_version(panel_id) # Retrive the latest panel version, using panel Id as an input

            if lastest_online_version == None: # If online version can't be accessed/return no data
                return f'The latest version of panel app was unable to be contacted, results are on valid from (lastupdate date)'
            elif query.get_db_latest_version(args["R code"]) != lastest_online_version: # If our version NOT same as panel app latest, then update database and continue
                # Update db
                return f'update the db! goes here!'

            else:
                patient_history = query.check_patient_history(args["Patient ID"], args["R code"]) # Returns all rows for a patient for a given Rcode
            if patient_history == None: # Checks if the response is empty ie - the patient_id isn't in the table
                return f"There is no record of patient {args["Patient ID"]} recieving {args["R code"]} within our records" # Return explanatory message
            else: # If patient_ID in table with the Rcode, find the difference between their most recent panel version & the current panel version
                database_version = query.get_db_latest_version(args["R code"])
                
                return f"{str(patient_history)}, ----->  {database_version} Display diffs below {len(args)}"
        
        
            
update_space = api.namespace('Update Patient Records', description='Update the Vimmo database with a patients test history')
update_parser = UpdateParser.create_parser()
@update_space.route("/update")
class UpdateClass(Resource):
    @api.doc(parser=update_parser)
    def get(self):
        args = update_parser.parse_args()
        
        ### Update functionality here ###
        return f"{args}"
        

    
