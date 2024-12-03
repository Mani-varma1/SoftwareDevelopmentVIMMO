# import unittest
# from unittest.mock import patch
# from flask import Flask
# from flask_restx import Api
# from vimmo.API.endpoints import panels_space, get_db
# from flask_testing import TestCase
#
#
# class TestPanelSearch(TestCase):
#     def create_app(self):
#         app = Flask(__name__)
#         app.register_blueprint(panels_space)  # Register your blueprint
#         return app
#
#     @patch('vimmo.API.endpoints.get_db')  # Mock the get_db method
#     def test_valid_rcode(self, mock_get_db):
#         # Mock database response
#         mock_cursor = mock_get_db.return_value.cursor.return_value
#         mock_cursor.execute.return_value.fetchall.return_value = [
#             ('1', 'R123', 'v1.0', 'HGNC:100', 'GeneA', 'SymA', '1', 100000, 200000)
#         ]
#
#         # Simulate the GET request
#         response = self.client.get('/panels?Rcode=R123')
#
#         # Assert the response status code and structure
#         self.assertEqual(response.status_code, 200)
#         response_json = response.json
#         self.assertIn('Rcode', response_json)
#         self.assertEqual(response_json['Rcode'], 'R123')
#         self.assertIn('Associated Gene Records', response_json)
#         self.assertEqual(len(response_json['Associated Gene Records']), 1)
#
#
#         # Assert that the mock database was called
#         mock_cursor.execute.assert_called_with(
#             '''
#             SELECT panel.Panel_ID, panel.rcodes, panel.Version, genes_info.HGNC_ID,
#                    genes_info.Gene_Symbol, genes_info.HGNC_symbol, genes_info.GRCh38_Chr,
#                    genes_info.GRCh38_start, genes_info.GRCh38_stop
#             FROM panel
#             JOIN panel_genes ON panel.Panel_ID = panel_genes.Panel_ID
#             JOIN genes_info ON panel_genes.HGNC_ID = genes_info.HGNC_ID
#             WHERE UPPER(panel.rcodes) = ?
#             ''', ('R123',)
#         )
#
#     @patch('vimmo.API.endpoints.get_db')
#     def test_invalid_rcode_format(self, mock_get_db):
#         # Simulate invalid 'Rcode' format
#         response = self.client.get('/panels?Rcode=invalidRcode')
#
#         # Assert the response status code and error message
#         self.assertEqual(response.status_code, 400)
#         self.assertIn('error', response.json)
#         self.assertEqual(response.json['error'], "Invalid format for 'Rcode': Must start with 'R' followed by digits.")
#
#     @patch('vimmo.API.endpoints.get_db')
#     def test_missing_rcode(self, mock_get_db):
#         # Simulate a request without 'Rcode'
#         response = self.client.get('/panels')
#
#         # Assert that the response indicates a missing 'Rcode' or incorrect query
#         self.assertEqual(response.status_code, 400)
#         self.assertIn('error', response.json)
#         self.assertEqual(response.json['error'], "At least one of 'Panel_ID', 'Rcode', or 'HGNC_ID' must be provided.")
#
#     @patch('vimmo.API.endpoints.get_db')
#     def test_no_matching_rcode(self, mock_get_db):
#         # Mock no results for a specific Rcode
#         mock_cursor = mock_get_db.return_value.cursor.return_value
#         mock_cursor.execute.return_value.fetchall.return_value = []
#
#         response = self.client.get('/panels?Rcode=R999')
#
#         self.assertEqual(response.status_code, 200)
#         response_json = response.json
#         self.assertIn('Rcode', response_json)
#         self.assertEqual(response_json['Rcode'], 'R999')
#         self.assertIn('Message', response_json)
#         self.assertEqual(response_json['Message'], 'No matches found for this rcode.')
#
