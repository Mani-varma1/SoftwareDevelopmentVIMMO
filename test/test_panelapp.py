# import unittest
# from unittest.mock import patch, Mock
# from vimmo.utils.panelapp import PanelAppClient, PanelAppAPIError
#
# class TestPanelAppClientInit(unittest.TestCase):
#     def test_default_base_url(self):
#         # Test initialization with the default base URL
#         client = PanelAppClient()
#         self.assertEqual(client.base_url, 'https://panelapp.genomicsengland.co.uk/api/v1/panels')
#
#     def test_custom_base_url(self):
#         # Test initialization with a custom base URL
#         custom_url = 'https://custom-url.com/api'
#         client = PanelAppClient(base_url=custom_url)
#         self.assertEqual(client.base_url, custom_url)
#
#
#
# if __name__ == '__main__':
#     unittest.main()


import unittest
from unittest.mock import patch, Mock
from vimmo.utils.panelapp import PanelAppClient, PanelAppAPIError


class TestPanelAppClient(unittest.TestCase):

    def setUp(self):
        # Set up a default instance of PanelAppClient for testing
        self.client = PanelAppClient()

    @patch('panelapp.PanelAppClient._check_response')  # Mock the _check_response method
    def test_get_genes_HUGO_success(self, mock_check_response):
        # Simulate a successful API response
        mock_check_response.return_value = {
            "results": [
                {"gene_data": {"gene_symbol": "GENE1"}},
                {"gene_data": {"gene_symbol": "GENE2"}},
                {"gene_data": {"gene_symbol": "GENE3"}}
            ]
        }

        # Call the get_genes_HUGO method
        rcode = "R123"
        confidence_level = 3
        result = self.client.get_genes_HUGO(rcode, confidence_level)

        # Assert the expected list of gene symbols is returned
        self.assertEqual(result, ["GENE1", "GENE2", "GENE3"])

        # Verify the URL was constructed correctly
        expected_url = f'{self.client.base_url}/{rcode}/genes/?confidence_level={confidence_level}'
        mock_check_response.assert_called_once_with(expected_url)

    @patch('panelapp.PanelAppClient._check_response')  # Mock the _check_response method
    def test_get_genes_HUGO_empty_results(self, mock_check_response):
        # Simulate an API response with no results
        mock_check_response.return_value = {"results": []}

        # Call the get_genes_HUGO method
        rcode = "R123"
        confidence_level = 3
        result = self.client.get_genes_HUGO(rcode, confidence_level)

        # Assert an empty list is returned
        self.assertEqual(result, [])

    @patch('panelapp.PanelAppClient._check_response')  # Mock the _check_response method
    def test_get_genes_HUGO_missing_gene_data(self, mock_check_response):
        # Simulate an API response with missing "gene_data"
        mock_check_response.return_value = {
            "results": [
                {"gene_data": {}},  # Missing "gene_symbol"
                {"gene_data": {"gene_symbol": "GENE2"}}
            ]
        }

        # Call the get_genes_HUGO method
        rcode = "R123"
        confidence_level = 3
        result = self.client.get_genes_HUGO(rcode, confidence_level)

        # Assert only the valid gene symbols are returned
        self.assertEqual(result, ["GENE2"])


if __name__ == '__main__':
    unittest.main()
