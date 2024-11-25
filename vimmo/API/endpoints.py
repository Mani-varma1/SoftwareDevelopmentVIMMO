
from flask import render_template, send_file
from flask_restx import Resource
from vimmo.API import api,get_db
from vimmo.utils.panelapp import  PanelAppClient
from vimmo.utils.variantvalidator import VarValClient, VarValAPIError
from vimmo.utils.parser import IDParser, PatientParser, DownloadParser
from vimmo.utils.arg_validator import validate_id_or_hgnc
from vimmo.db.db import PanelQuery
from io import StringIO, BytesIO
import pandas as pd

panel_app_client = PanelAppClient()



panels_space = api.namespace('panels', description='Return panel data provided by the user')
id_parser = IDParser.create_parser()
# Define Panel Endpoint
@panels_space.route('/panels')
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
        
        if args.get("ID",None):
            panel_data = query.get_panel_data(ID=args.get("ID"),matches=args.get("Similar_Matches"))
            return panel_data
        else:
            panels_returned = query.get_panels_from_gene(hgnc_id=args.get("HGNC_ID"),matches=args.get("Similar_Matches"))
            return panels_returned





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
            validate_id_or_hgnc(args)
        except ValueError as e:
            return {"error": str(e)}, 400
        

        gene_query = args.get("HGNC_ID")
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
        filename = f"{gene_query.replace('|', '_')}_{genome_build}_mane_select.bed"

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

        gene_list = panel_app_client.get_genes(rcode)
        return {
            f"Paitned ID: {args['Patient_ID ']} List of genes in {rcode}" : gene_list
        }