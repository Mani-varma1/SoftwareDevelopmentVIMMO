
from flask_restx import Resource
from APIapp import api
from utils.panelapp import  PanelAppClient
import requests

panel_app_client = PanelAppClient()


VIMMO_space = api.namespace('VIMMO', description='Return a name provided by the user')
@VIMMO_space.route("/<string:rcode>")
class NameClass(Resource):
    def get(self, rcode):
        gene_list = gene_list = panel_app_client.get_genes(rcode)
        return {
            f"List of genes in {rcode}" : gene_list
        }