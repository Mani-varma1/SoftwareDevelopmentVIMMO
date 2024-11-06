from flask import Flask
from flask_restx import Api

app = Flask(__name__)
api = Api(app=app)

# Import the routes to register them
from APIapp import endpoints