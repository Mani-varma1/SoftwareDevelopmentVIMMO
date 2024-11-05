from flask import Flask
from flask_restx import Api, Resource
import requests


# Import modules
from flask import Flask
from flask_restx import Api, Resource

# Define the application as a Flask app with the name defined by __name__ (i.e. the name of the current module)
# Most tutorials define application as "app", but I have had issues with this when it comes to deployment,
# so application is recommended
application = Flask(__name__)

# Define the API as api
api = Api(app = application)

panelapp_space = api.namespace('PanelApp', description='Return a name provided by the user')
@panelapp_space.route("/<string:rcode>")
class NameClass(Resource):
    def get(self, rcode):
        rcode = rcode
        # genes = db.search(rcode)
        return {
            "List of genes" : rcode
        }


# Allows app to be run in debug mode
if __name__ == '__main__':
    application.debug = True # Enable debugging mode
    application.run(host="127.0.0.1", port=5000) # Specify a host and port fot the app
