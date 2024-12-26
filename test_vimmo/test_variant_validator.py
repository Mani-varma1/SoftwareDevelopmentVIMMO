"""
test_variant_validator.py - Test Suite for VariantValidator Client

This module contains tests for the VariantValidator client functionality while
handling Python's module loading complexities. The key challenge addressed here
is managing circular imports in a Flask application with multiple interdependent
modules.

Module Loading Process:
When Python imports modules, it follows a specific sequence:
1. Start loading the requested module
2. Process its imports from top to bottom
3. If an imported module tries to import something that's still loading,
   Python encounters a circular import error

The Problem:
In our application, we have the following import chain:
- variantvalidator.py needs get_db from vimmo.API
- vimmo.API/__init__.py imports endpoints.py
- endpoints.py imports VarValClient from variantvalidator.py

This creates a circular dependency that fails when testing because:
- Tests try to import VarValClient directly
- This triggers the import chain before the Flask app is initialized
- The partial imports cause Python to raise ImportError

The Solution:
We solve this by following the same initialization order as our main application:
1. First, we mock the database connection
2. Then we import the Flask app, which sets up the proper environment
3. Only after that do we import VarValClient

This mirrors how our production application loads modules and prevents
circular import issues while maintaining proper test isolation.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock, call
from io import BytesIO
import pandas as pd
from vimmo.API import app  # Ensures Flask/DB init order
from vimmo.utils.variantvalidator import VarValClient, VarValAPIError


class TestVarValClient(unittest.TestCase):
    """
    Test suite for the VariantValidator API client.
    
    This class tests the functionality of the VarValClient including:
    - API communication
    - Data parsing and transformation
    - Error handling
    - BED file generation
    
    Each test method focuses on a specific aspect of the client's functionality
    while mocking external dependencies to ensure reliable testing.
    """

    def setUp(self):
        """
        Initialize test environment before each test.
        Creates a client instance and sets up common test data.
        """
        self.client = VarValClient()

    @patch('requests.get')
    def test_check_response_success(self, mock_get):
        """
        Test successful API response handling.
        Verifies that valid API responses are properly processed and returned.
        """
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {"test": "data"}
        
        result = self.client._check_response("test_url")
        self.assertEqual(result, {"test": "data"})

    @patch('requests.get', side_effect=Exception("Connection failed"))
    def test_check_response_connection_error(self, mock_get):
        """
        Test handling of connection failures.
        Ensures appropriate error handling when network connection fails.
        """
        with self.assertRaises(VarValAPIError) as context:
            self.client._check_response("test_url")
        self.assertIn("Failed to connect", str(context.exception))

    @patch('requests.get')
    def test_check_response_non_200(self, mock_get):
        """
        Test handling of non-200 status codes.
        Ensures that a VarValAPIError is raised if the response is not OK.
        """
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 404
        
        with self.assertRaises(VarValAPIError) as context:
            self.client._check_response("test_url")
        self.assertIn("Failed to get data from VarVal API with Status code:404", str(context.exception))

    def test_custom_sort(self):
        """
        Test the custom sorting function for BED file entries.
        
        Verifies correct sorting of:
        - Chromosome numbers
        - X and Y chromosomes
        - Error cases
        - Start/end coordinates
        """
        test_data = pd.DataFrame([
            {'chrom': 'chr1', 'start': '1000', 'end': '2000'},
            {'chrom': 'chrX', 'start': '500', 'end': '1500'},
            {'chrom': 'chr2', 'start': '750', 'end': '1750'},
            {'chrom': 'NoRecord', 'start': 'Error', 'end': 'Error'}
        ])

        # Test individual sorting keys
        self.assertEqual(
            self.client.custom_sort(test_data.iloc[0]),
            (1, 1000, 2000)
        )
        self.assertEqual(
            self.client.custom_sort(test_data.iloc[1]),
            (23, 500, 1500)  # 'X' chromosome -> 23
        )
        self.assertEqual(
            self.client.custom_sort(test_data.iloc[2]),
            (2, 750, 1750)
        )
        self.assertEqual(
            self.client.custom_sort(test_data.iloc[3]),
            (float('inf'), float('inf'), float('inf'))
        )

    @patch('requests.get')
    def test_get_gene_data_success(self, mock_get):
        """
        Test successful retrieval of gene data via get_gene_data.
        Mocks requests.get to return a successful response.
        """
        mock_response_data = [{"mock": "gene_data"}]
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response_data
        
        # 1) Call with BRCA1
        self.client.get_gene_data(
            gene_query="BRCA1",
            genome_build="GRCh38",
            transcript_set="all",
            limit_transcripts="mane_select"
        )

        # 2) Call with HGNC:1100
        self.client.get_gene_data(
            gene_query="HGNC:1100",
            genome_build="GRCh38",
            transcript_set="all",
            limit_transcripts="mane_select"
        )

        # The two expected function calls
        expected_url_brca = (
            "https://rest.variantvalidator.org/VariantValidator/tools/"
            "gene2transcripts_v2/BRCA1/mane_select/all/GRCh38"
        )
        expected_url_hgnc = (
            "https://rest.variantvalidator.org/VariantValidator/tools/"
            "gene2transcripts_v2/HGNC%3A1100/mane_select/all/GRCh38"
        )

        # Check only the function calls, ignoring the call().json() part
        expected_calls = [
            unittest.mock.call(expected_url_brca),
            unittest.mock.call(expected_url_hgnc),
        ]
        self.assertEqual(mock_get.call_args_list, expected_calls)

    @patch('requests.get')
    def test_get_gene_data_non_200(self, mock_get):
        """
        Test get_gene_data raises VarValAPIError when the API returns non-200.
        """
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 500

        with self.assertRaises(VarValAPIError) as context:
            self.client.get_gene_data("BRCA2")
        self.assertIn("Failed to get data from VarVal API with Status code:500", str(context.exception))

    @patch('builtins.open', new_callable=mock_open, read_data="HGNC:123\nHGNC:999\n")
    @patch('vimmo.utils.variantvalidator.Query')
    @patch('vimmo.utils.variantvalidator.get_db')
    def test_get_hgnc_ids_with_replacements(self, mock_get_db, mock_query_cls, mock_file):
        """
        Test that get_hgnc_ids_with_replacements correctly replaces 
        problematic HGNC IDs with their symbols if found in the DB.
        """
        # Mock the DB connection
        mock_db_instance = MagicMock()
        mock_db_instance.conn = "fake_connection"
        mock_get_db.return_value = mock_db_instance

        # Mock the query object to return pairs of (hgnc_id, hgnc_symbol)
        mock_query_instance = MagicMock()
        mock_query_instance.get_gene_symbol.return_value = [("HGNC:123", "BRCA1_symbol")]
        mock_query_cls.return_value = mock_query_instance
        
        # Call the method
        gene_query = ["HGNC:123", "HGNC:456"]
        result = self.client.get_hgnc_ids_with_replacements(gene_query)

        # "HGNC:123" should be replaced by "BRCA1_symbol"
        # "HGNC:456" remains as is
        self.assertIn("BRCA1_symbol", result)
        self.assertIn("HGNC:456", result)

        # Ensure the DB was called only for the problematic genes
        mock_query_instance.get_gene_symbol.assert_called_once_with(["HGNC:123"])

    @patch('builtins.open', new_callable=mock_open, read_data="")
    @patch('vimmo.utils.variantvalidator.Query')
    @patch('vimmo.utils.variantvalidator.get_db')
    @patch('requests.get')
    def test_parse_to_bed_success(self, mock_get, mock_get_db, mock_query_cls, mock_file):
        """
        Test parse_to_bed outputs valid BED content from the API data.
        """
        # Mock DB/Query for get_hgnc_ids_with_replacements
        mock_db_instance = MagicMock()
        mock_db_instance.conn = "fake_connection"
        mock_get_db.return_value = mock_db_instance

        mock_query_instance = MagicMock()
        mock_query_instance.get_gene_symbol.return_value = []
        mock_query_cls.return_value = mock_query_instance

        # Mock API response for get_gene_data
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = [
            {
                "requested_symbol": "BRCA1",
                "current_symbol": "BRCA1",
                "transcripts": [
                    {
                        "annotations": {
                            "chromosome": "17"
                        },
                        "reference": "RefSeq",
                        "genomic_spans": {
                            "NM_007294.3": {
                                "orientation": 1,
                                "exon_structure": [
                                    {
                                        "exon_number": 1,
                                        "genomic_start": 43044295,
                                        "genomic_end": 43044837
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        ]
                
        # Call parse_to_bed
        bed_io = self.client.parse_to_bed(gene_query=["HGNC:1100"])  # e.g., "BRCA1"
        self.assertIsInstance(bed_io, BytesIO)
        
        # Read the resulting BED data
        bed_data = bed_io.read().decode('utf-8').strip().split('\n')
        
        # Expect one line: chr17 <start> <end> BRCA1_exon1_RefSeq +
        # Because orientation=1 -> strand '+'
        expected_line = "chr17\t43044295\t43044837\tBRCA1_exon1_RefSeq\t+"
        self.assertEqual(len(bed_data), 1)
        self.assertEqual(bed_data[0], expected_line)


if __name__ == '__main__':
    unittest.main()