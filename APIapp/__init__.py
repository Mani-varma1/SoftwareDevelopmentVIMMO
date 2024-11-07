from flask import Flask  # Import Flask to create a web application
from flask_restx import Api  # Import the Api class from flask_restx to manage the API

# Initialize the Flask app
app = Flask(__name__)  

# Initialize the API with the Flask app
api = Api(app=app)

# Import endpoints to register them with the app and API
from APIapp import endpoints