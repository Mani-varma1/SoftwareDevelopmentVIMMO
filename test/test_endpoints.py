import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from vimmo.API.endpoints import panels_space, get_db
from flask_testing import TestCase


class TestPanelSearch(TestCase):
    def create_app(self):
        """Create and configure the Flask application for testing."""
        app = Flask(__name__)
        api = Api(app)
        api.add_namespace(panels_space)
        return app

    @patch('vimmo.API.endpoints.get_db')
    def test_valid_rcode(self, mock_get_db):
        """Test a valid Rcode query."""
        mock_cursor = MagicMock()
        mock_get_db.return_value.cursor.return_value = mock_cursor


        mock_cursor.fetchall.return_value = [
            ('1', 'R123', 'v1.0', 'HGNC:100', 'GeneA', 'SymA', '1', 100000, 200000)
        ]

        # Simulate the GET request with a valid Rcode
        response = self.client.get('/panels?Rcode=R123')

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Assert the response JSON structure and content
        response_json = response.json
        self.assertIn('Rcode', response_json)
        self.assertEqual(response_json['Rcode'], 'R123')
        self.assertIn('Associated Gene Records', response_json)
        self.assertEqual(len(response_json['Associated Gene Records']), 1)

        # Assert that the database query was executed correctly
        mock_cursor.execute.assert_called_with(
            '''
            SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID,
                   genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr,
                   genes_info.GRCh38_start, genes_info.GRCh38_stop
            FROM panel
            JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
            JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
            WHERE UPPER(panel.rcodes) = ?
            ''', ('R123',)
        )

    @patch('vimmo.API.endpoints.get_db')
    def test_invalid_rcode_format(self, mock_get_db):
        """Test an invalid Rcode format."""
        # Simulate the GET request with an invalid Rcode format
        response = self.client.get('/panels?Rcode=invalidRcode')

        # Assert the response status code and error message
        self.assertEqual(response.status_code, 400)
        response_json = response.json
        self.assertIn('error', response_json)
        self.assertEqual(response_json['error'], "Invalid format for 'Rcode': Must start with 'R' followed by digits.")

    @patch('vimmo.API.endpoints.get_db')
    def test_missing_rcode(self, mock_get_db):
        """Test a request with no Rcode."""
        # Simulate the GET request without any Rcode
        response = self.client.get('/panels')

        # Assert the response status code and error message
        self.assertEqual(response.status_code, 400)
        response_json = response.json
        self.assertIn('error', response_json)
        self.assertEqual(response_json['error'], "At least one of 'Panel_ID', 'Rcode', or 'HGNC_ID' must be provided.")

    @patch('vimmo.API.endpoints.get_db')
    def test_no_matching_rcode(self, mock_get_db):
        """Test a valid Rcode query with no matching records."""
        # Mock the database connection and cursor
        mock_cursor = MagicMock()
        mock_get_db.return_value.cursor.return_value = mock_cursor

        # Mock the database response for no matches
        mock_cursor.fetchall.return_value = []

        # Simulate the GET request with a valid Rcode that has no matches
        response = self.client.get('/panels?Rcode=R999')

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Assert the response JSON structure and content
        response_json = response.json
        self.assertIn('Rcode', response_json)
        self.assertEqual(response_json['Rcode'], 'R999')
        self.assertIn('Message', response_json)
        self.assertEqual(response_json['Message'], 'No matches found for this rcode.')

if __name__ == '__main__':
    unittest.main()
