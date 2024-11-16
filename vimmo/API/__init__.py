from flask import Flask, g
from flask_restx import Api
from vimmo.db.db import Database

app = Flask(__name__)
api = Api(app=app)


def get_db():
    # If a database connection does not exist in the current request context, create one
    if 'db' not in g:
        g.db = Database()
        g.db.connect()
    return g.db

@app.teardown_appcontext
def shutdown_session(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Import the routes to register them
from vimmo.API import endpoints