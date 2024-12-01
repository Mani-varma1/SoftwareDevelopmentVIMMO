
from flask import send_file
from flask_restx import Resource
from vimmo.API import api,get_db
from vimmo.utils.panelapp import  PanelAppClient
from vimmo.utils.variantvalidator import VarValClient, VarValAPIError
from vimmo.utils.parser import IDParser, PatientParser, DownloadParser, LocalDownloadParser
from vimmo.utils.arg_validator import validate_panel_id_or_Rcode_or_hgnc
from vimmo.db.db import PanelQuery


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
        matches=args.get("Similar_Matches",None)
        HGNC_ID=args.get("HGNC_ID",None)


        # Retrieve the database connection
        db = get_db()
        # Initialize a query object with the database connection
        query = PanelQuery(db.conn)
        
        if not HGNC_ID:
            gene_query=query.get_gene_list(panel_id,r_code,matches)
            if "Message" in gene_query:
                return gene_query
        else:
            gene_query=HGNC_ID
            

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





local_download_parser=LocalDownloadParser.create_parser()
@panels_space.route('/download/local')
class PanelDownload(Resource):
    @api.doc(parser=local_download_parser)
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
        matches=args.get("Similar_Matches",None)
        HGNC_ID=args.get("HGNC_ID",None)


        # Retrieve the database connection
        db = get_db()
        # Initialize a query object with the database connection
        query = PanelQuery(db.conn)
        gene_query=query.get_gene_list(panel_id,r_code,matches,HGNC_ID)
        genome_build = args.get('genome_build', 'GRCh38')
        bed_file="hi"



        # Generate a meaningful filename for the download
        if panel_id:
            filename = f"{panel_id}_{genome_build}_Gencode.bed"
        elif r_code:
            filename = f"{r_code}_{genome_build}_Gencode.bed"
        else:
            filename = f"Genes_{genome_build}_Gencode.bed"

        # Return the BED file as a downloadable response
        return send_file(
            bed_file,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )



    


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
    
