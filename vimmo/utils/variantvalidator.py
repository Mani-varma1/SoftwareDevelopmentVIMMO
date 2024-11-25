import requests
from urllib.parse import quote
import pandas as pd
from io import BytesIO

class VarValAPIError(Exception):
    """Custom exception for errors related to the PanelApp API."""
    pass


class VarValClient:
    def __init__(self, base_url='https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2'):
        """
        Initialize the VariantValidator client.

        Parameters:
        - base_url (str): Base URL for the VariantValidator API.
        """

        self.base_url = base_url

    def _check_response(self, url):
        """
        Sends a GET request to the specified URL and validates the response.

        Parameters:
        - url (str): URL to send the GET request to.

        Returns:
        - dict: Parsed JSON response from the API.

        Raises:
        - VarValAPIError: If the request fails or the status code is not 200.
        """
        try:
            response = requests.get(url)
            print("Hi")
        except :
            raise VarValAPIError(f"Failed to get data from PanelApp API. Status code: {response.status_code}")
        else:
            return response.json()

    def get_gene_data(self, gene_query, genome_build='GRCh38', transcript_set='all', limit_transcripts='all'):
        """
        Fetches gene data from the VariantValidator API.

        Parameters:
        - gene_query (str): Gene identifier (HGNC ID, symbol, or transcript ID).
        - genome_build (str): Genome build version (e.g., 'GRCh37' or 'GRCh38').
        - transcript_set (str): Specifies the transcript set ('refseq', 'ensembl', or 'all').
        - limit_transcripts (str): Specifies transcript filtering criteria ('mane', 'select', or 'all').

        Returns:
        - dict: JSON response containing gene data.

        Raises:
        - VarValAPIError: If the API request fails or returns an error response.
        """
        # Encode URL components to ensure compatibility
        encoded_gene_query = quote(gene_query)
        encoded_transcript_set = quote(transcript_set)
        encoded_limit_transcripts = quote(limit_transcripts)
        encoded_genome_build = quote(genome_build)

        # Construct the full URL
        url = (
            f"{self.base_url}/"
            f"{encoded_gene_query}/"
            f"{encoded_limit_transcripts}/"
            f"{encoded_transcript_set}/"
            f"{encoded_genome_build}"
        )

        # Make the request and return the response
        return self._check_response(url)
    

    def parse_to_bed(self, gene_query, genome_build='GRCh38', transcript_set='all', limit_transcripts='mane_select'):
        """
        Fetches gene data from the API and converts it to BED file format.

        Parameters:
        - gene_query (str): Gene identifier for querying (HGNC ID, symbol, or transcript ID).
        - genome_build (str): Genome build version (e.g., 'GRCh37' or 'GRCh38'). Defaults: GRCh38
        - transcript_set (str): Transcript set to use (e.g., 'refseq', 'ensembl', 'all'). Defaults: all
        - limit_transcripts (str): Filter for specific transcript sets ('mane', 'select', 'mane_select'). Defaults: mane_select

        Returns:
        - BytesIO: BED file content ready to be sent as a response.

        Raises:
        - VarValAPIError: If fetching or processing gene data fails.
        """
        # Map user-friendly transcript options to API-compatible values
        limit_transcripts_map = {
            'mane_select + mane_plus_clinical': 'mane',
            'mane_select': 'mane_select',
            'canonical': 'select'
        }
        limit_transcripts = limit_transcripts_map.get(limit_transcripts, limit_transcripts)
        print("point 1")

        try:
            # Fetch gene data from the API
            gene_data = self.get_gene_data(
                gene_query=gene_query,
                genome_build=genome_build,
                transcript_set=transcript_set,
                limit_transcripts=limit_transcripts
            )
        except VarValAPIError as e:
            raise VarValAPIError(f"Error fetching data: {str(e)}")

        # Parse the gene data into BED format
        bed_rows = []
        for gene in gene_data:
            chromosome = f"chr{gene['transcripts'][0]['annotations']['chromosome']}"
            for transcript in gene.get('transcripts', []):
                reference = transcript.get('reference', '.')
                genomic_spans = transcript.get('genomic_spans', {})
                for accession, spans in genomic_spans.items():
                    orientation = '+' if spans.get('orientation') == 1 else '-'
                    for exon in spans.get('exon_structure', []):
                        bed_rows.append({
                            'chrom': chromosome,
                            'start': exon['genomic_start'],
                            'end': exon['genomic_end'],
                            'name': f"{gene['current_symbol']}_exon{exon['exon_number']}_{reference}",
                            'strand': orientation
                        })

        # Convert rows into a DataFrame
        bed_df = pd.DataFrame(bed_rows)

        # Write the DataFrame to a BED file (BytesIO)
        output = BytesIO()
        bed_string = bed_df.to_csv(
            sep='\t',
            index=False,
            header=False,
            columns=['chrom', 'start', 'end', 'name', 'strand']
        )
        output.write(bed_string.encode('utf-8'))
        output.seek(0)
        return output