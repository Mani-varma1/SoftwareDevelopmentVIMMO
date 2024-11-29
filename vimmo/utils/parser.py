from flask_restx import reqparse, inputs

class IDParser:
    """Parser for handling panel ID, Rcode, and HGNC ID arguments."""
    
    @staticmethod
    def create_parser():
        """Create and return a request parser for ID-related arguments."""
        parser = reqparse.RequestParser()
        
        # Argument for Panel_ID
        parser.add_argument(
            'Panel_ID',
            type=int,
            help="Provide Panel_ID. Leave blank if using 'Rcode' or 'HGNC_ID'.",
            required=False
        )
        
        # Argument for Rcode
        parser.add_argument(
            'Rcode',
            type=str,
            help="Provide Rcode. Leave blank if using 'Panel_ID' or 'HGNC_ID'.",
            required=False
        )
        
        # Argument for HGNC_ID
        parser.add_argument(
            'HGNC_ID',
            type=str,
            help="Provide HGNC ID. Leave blank if using 'Rcode' or 'Panel_ID'.",
            required=False
        )
        
        # Argument for Similar_Matches (boolean)
        parser.add_argument(
            'Similar_Matches',
            type=inputs.boolean,
            help="Select true to get similarly matched IDs. Use 'true' or 'false' (case-insensitive).",
            required=False,
            default=False
        )
        
        return parser


class PatientParser:
    """Parser for handling patient-related arguments."""
    
    @staticmethod
    def create_parser():
        """Create and return a request parser for patient-related arguments."""
        parser = reqparse.RequestParser()
        
        # Argument for Patient ID
        parser.add_argument(
            '-f',
            type=str,
            help='Type in Patient ID'
        )
        
        # Argument for R code
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
            required=True,
            default='GRCh38'
        )
        parser.add_argument(
            'transcript_set',
            type=str,
            choices=['refseq', 'ensembl', 'all'],
            help="Specify the transcript set (refseq, ensembl, or all).",
            required=True,
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
                "'canonical' for canonical transcripts."
            ),
            required=True,
            default='mane_select'
        )

        return parser