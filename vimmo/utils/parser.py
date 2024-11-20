from flask_restx import reqparse, inputs

class IDParser:
    """Parser for handling panel ID and HGNC ID arguments."""
    @staticmethod
    def create_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'Panel_ID',
            type=int,  # Changed to int
            help="Provide Panel_ID. Leave blank if using 'Rcode' or 'HGNC_ID'.",
            required=False
        )
        parser.add_argument(
            'Rcode',
            type=str,  # Added missing comma
            help="Provide Rcode. Leave blank if using 'Panel_ID' or 'HGNC_ID'.",
            required=False  # Added for consistency
        )
        parser.add_argument(
            'HGNC_ID',
            type=str,
            help="Provide HGNC ID. Leave blank if using 'Rcode' or 'Panel_ID'.",
            required=False
        )
        parser.add_argument(
            'Similar_Matches',
            type=inputs.boolean,  # Use flask_restx.inputs.boolean instead of bool
            help="Select true to get similarly matched IDs. Use 'true' or 'false' (case-insensitive).",
            required=False,
            default=False
        )
        return parser

class PatientParser:
    """Parser for handling patient-related arguments."""
    @staticmethod
    def create_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            '-f',
            type=str,
            help='Type in Patient ID or R code'
        )
        parser.add_argument(
            'R code',
            type=str,
            help='Type in R code'
        )
        return parser
