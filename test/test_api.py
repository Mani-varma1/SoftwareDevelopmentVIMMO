# # test/test_api.py
#
# import unittest
# from unittest.mock import patch
# from vimmo.API import app
#
# class TestAPI(unittest.TestCase):
#     def setUp(self):
#         self.app = app.test_client()
#         self.app.testing = True
#
#     # @patch('APIapp.endpoints.requests.get')
#     # def test_get_genes_success(self, mock_get):
#     #     # Mock the JSON response from the requests.get call
#     #     mock_response = {
#     #         "results": [
#     #             {"gene_data": {"gene_symbol": "BRCA1"}},
#     #             {"gene_data": {"gene_symbol": "TP53"}}
#     #         ]
#     #     }
#     #     mock_get.return_value.json.return_value = mock_response
#
#     #     rcode = ''  # Example RCode
#     #     response = self.app.get(f'/PanelApp/{rcode}')
#     #     self.assertEqual(response.status_code, 200)
#     #     data = response.get_json()
#     #     expected_data = {
#     #         f"List of genes in {rcode}": ["BRCA1", "TP53"]
#     #     }
#     #     self.assertEqual(data, expected_data)
#
#     def test_get_genes_no_results(self):
#         rcode = '1111111'  # Example RCode with no results
#         response = self.app.get(f'/VIMMO/{rcode}')
#         self.assertEqual(response.status_code, 200)
#         data = response.get_json()
#         expected_data = {'List of genes in 1111111': []}
#         self.assertEqual(data, expected_data)
#
#     def test_invalid_route(self):
#         response = self.app.get('/ljzxcvnjhsbvd')
#         self.assertEqual(response.status_code, 404)
#
# if __name__ == '__main__':
#     unittest.main()