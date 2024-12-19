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
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except (requests.RequestException, ValueError):
            raise PanelAppAPIError("An error occurred while accessing or processing data from the PanelApp API.")


    def get_genes_HUGO(self, rcode, confidence_level=3):
        '''
        Query PanelApp API based on RCode --> return list of genes (HUGO gene symbols) with a specified confidence level.
        '''
        url = f'{self.base_url}/{rcode}/genes/?confidence_level={confidence_level}'
        json_data = self._check_response(url)
        gene_symbols = [entry["gene_data"]["gene_symbol"] for entry in json_data.get("results", [])]
        return gene_symbols
    
    def get_genes_HGNC(self, rcode, confidence_level=3):
        """
        Query PanelApp API base on Rcode --> return list of genes (HGNC id) with a specified confidence level.
        """
        url = f'{self.base_url}/{rcode}/genes/?confidence_level={confidence_level}'
        json_data = self._check_response(url)
        gene_symbols = [entry["gene_data"]["hgnc_id"] for entry in json_data.get("results", [])]
        return gene_symbols

    def get_latest_online_version(self, panel_id: str) -> str: 
        """
        Returns the most recent signedoff panel version from the panelapp api

        Parameters
        ----------
        panel_id : str
        The panel to search for in the panelapp database

        Returns
        -------
        version: str
        The latest  version for the most recent GMS signedoff panelapp panel

        Notes
        -----
        - This function substitues the input panel id into the signedoff URL
        - Using the response module, sends and recieves a GET HTTP request and response
        - It extracts the .json response format
        - Indexs the results nested dictionary, and extracts the 'version'

        Example
        -----
        User UI input: R208
        Query class method: rcode_to_panelID(R208) -> 635 # converts rcode to panel_id (see db.py)
        get_latest_online_version(635) -> 2.5
        
        Here 2.5 is the version of R208, as of (26/11/24)
        """
        
        url = f'{self.base_url}/signedoff/?panel_id={panel_id}&display=latest' # Set the URL 
        json_data = self._check_response(url) # Send get request to URL, if 200 return json format of the response
        
        try:
        # Safely extract the version
            version_value = json_data["results"][0]["version"] # Extract the version number from the json response
            version = float(version_value)

        except:
            return KeyError({"Error":"Invalid or missing rcode. Please check the R code at 'https://panelapp.genomicsengland.co.uk/panels/'"})

        else:
            return version
    

    def dowgrade_records(self, panel_id: str, version:str ) -> str: 
        """
        Returns the most recent signedoff panel version from the panelapp api

        Parameters
        ----------
        panel_id : str
        The panel to search for in the panelapp database

        Returns
        -------
        version: str
        The latest  version for the most recent GMS signedoff panelapp panel

        Notes
        -----
        - This function substitues the input panel id into the signedoff URL
        - Using the response module, sends and recieves a GET HTTP request and response
        - It extracts the .json response format
        - Indexs the results nested dictionary, and extracts the 'version'

        Example
        -----
        User UI input: R208
        Query class method: rcode_to_panelID(R208) -> 635 # converts rcode to panel_id (see db.py)
        get_latest_online_version(635) -> 2.5
        
        Here 2.5 is the version of R208, as of (26/11/24)
        """
        url = f'{self.base_url}/{panel_id}/?version={version}' # Set the URL
        print(url) 
        json_data = self._check_response(url) # Send get request to URL, if 200 return json format of the response
        return json_data
        # try:
            
        # except (KeyError, ValueError):
        #     print("Invalid or missing version. Please check the R code at 'https://panelapp.genomicsengland.co.uk/panels/'")
        #     version = None
        
        # return version