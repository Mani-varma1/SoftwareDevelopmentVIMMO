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
    



class DownloadParser:
    """Parser for handling download-related arguments."""

    @staticmethod
    def create_parser():
        parser = reqparse.RequestParser()

        id_parser = IDParser.create_parser()
        for arg in id_parser.args:
            parser.add_argument(**arg.__dict__)

        # Add additional arguments specific to the download functionality
        parser.add_argument(
            'genome_build',
            type=str,
            choices=['GRCh37', 'GRCh38'],
            help="Specify the genome build (GRCh37 or GRCh38).",
            required=False,
            default='GRCh38'
        )
        parser.add_argument(
            'transcript_set',
            type=str,
            choices=['refseq', 'ensembl', 'all'],
            help="Specify the transcript set (refseq, ensembl, or all).",
            required=False,
            default='all'
        )
        parser.add_argument(
            'limit_transcripts',
            type=str,
            choices=['mane_select + mane_plus_clinical', 'mane_select', 'canonical'],
            help=(
                "Limit transcripts to specific categories: "
                "'mane_select + mane_plus_clinical' for MANE Select and Mane Plus Clinical, "
                "'mane_select' for MANE Select only, "
                "'all' for all transcripts."
            ),
            required=False,
            default='all'
        )

        return parser