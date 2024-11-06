import requests

class PanelAppAPIError(Exception):
    """Custom exception for errors related to the PanelApp API."""
    pass


class PanelAppClient:
    def __init__(self, base_url='https://panelapp.genomicsengland.co.uk/api/v1/panels'):
        self.base_url = base_url

    def _check_response(self, url):
        '''
        Checks the HTTP response status code.
        Raises PanelAppAPIError if status code is not 200.
        '''
        try:
            response = requests.get(url)
        except :
            raise PanelAppAPIError(f"Failed to get data from PanelApp API. Status code: {response.status_code}")
        else:
            return response.json()

    def get_genes(self, rcode, confidence_level=3):
        '''
        Query PanelApp API based on RCode --> return list of genes with specified confidence level.
        '''
        url = f'{self.base_url}/{rcode}/genes/?confidence_level={confidence_level}'
        json_data = self._check_response(url)
        gene_symbols = [entry["gene_data"]["gene_symbol"] for entry in json_data.get("results", [])]
        return gene_symbols