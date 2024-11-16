from flask_restx import reqparse,inputs

class IDParser:
    """Parser for handling panel ID and HGNC ID arguments."""
    @staticmethod
    def create_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'ID',
            type=str,
            help="Provide Panel ID or R-code. Leave blank if using 'HGNC_ID'.",
            required=False
        )
        parser.add_argument(
            'HGNC_ID',
            type=str,
            help="Provide HGNC ID. Leave blank if using 'ID'.",
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