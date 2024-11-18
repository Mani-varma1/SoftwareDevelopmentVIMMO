
from flask import render_template, send_file
from flask_restx import Resource
from vimmo.API import api,get_db
from vimmo.utils.panelapp import  PanelAppClient
from vimmo.utils.parser import IDParser, PatientParser
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


@panels_space.route('/download')
class PanelDownload(Resource):
    @api.doc(parser=id_parser)  # Hide from Swagger UI but keep endpoint accessible
    def get(self):
        """Download panel data as BED file"""
        args = id_parser.parse_args()
        
        # Dummy data structure mimicking your panel data
        dummy_data = {
            "panel_id": "123",
            "genes": [
                {
                    "gene_symbol": "BRCA1",
                    "chromosome": "chr17",
                    "start": 43044295,
                    "end": 43125364,
                    "strand": "+"
                },
                {
                    "gene_symbol": "BRCA2",
                    "chromosome": "chr13",
                    "start": 32315474,
                    "end": 32399672,
                    "strand": "-"
                },
                {
                    "gene_symbol": "TP53",
                    "chromosome": "chr17",
                    "start": 7571720,
                    "end": 7590868,
                    "strand": "+"
                }
            ]
        }
        
        # Convert to BED format
        bed_rows = []
        for gene in dummy_data["genes"]:
            bed_rows.append({
                'chrom': gene.get('chromosome', '.'),
                'start': gene.get('start', 0),
                'end': gene.get('end', 0),
                'name': f"{gene.get('gene_symbol', '.')}_{dummy_data['panel_id']}",
                'score': 1000,
                'strand': gene.get('strand', '.')
            })
        
        bed_df = pd.DataFrame(bed_rows)
        
        # Create a BytesIO object
        output = BytesIO()
        
        # Write DataFrame to string buffer
        bed_string = bed_df.to_csv(
            sep='\t',
            index=False,
            header=False,
            columns=['chrom', 'start', 'end', 'name', 'score', 'strand']
        )
        
        # Convert string to bytes and write to BytesIO
        output.write(bed_string.encode('utf-8'))
        output.seek(0)
        
        filename = f"panel_{'_'.join(filter(None, [args.get('ID'), args.get('HGNC_ID')]))}.bed"
        
        return send_file(
            output,
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