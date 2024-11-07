from flask_restx import Resource  # Import Resource to create RESTful resources
from APIapp import api  # Import the `api` object, assumed to be initialized in APIapp as an Api instance
from utils.panelapp import PanelAppClient  # Import PanelAppClient, a custom client to interact with PanelApp
import requests  # Import requests if additional HTTP requests are required within the resource (may be redundant here)

# Instantiate the PanelAppClient to interact with PanelApp API
panel_app_client = PanelAppClient()

# Define a namespace for grouping related endpoints under 'VIMMO'
VIMMO_space = api.namespace('VIMMO', description='Return a name provided by the user')

# Define a route in the VIMMO namespace, expecting a string variable 'rcode' in the URL
@VIMMO_space.route("/<string:rcode>")
class NameClass(Resource):
    def get(self, rcode):
        # Use the PanelAppClient instance to fetch a list of genes based on the provided rcode
        gene_list = panel_app_client.get_genes(rcode)
        
        # Return a JSON response with a message and the list of genes
        return {
            f"List of genes in {rcode}": gene_list
        }