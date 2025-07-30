# This script runs automatically when our `loginapp` module is first loaded,
# and handles all the setup for our Flask app.
from flask import Flask

app = Flask(__name__)

app.secret_key = 'Example Secret Key (CHANGE THIS TO YOUR OWN SECRET KEY!)'

# Set up database connection.
from app import connect
from app import db
db.init_db(app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname,
           connect.dbport)

# Include all modules that define our Flask route-handling functions.
from app import auth
from app import student
from app import employer
from app import admin
from app import common

# cache busting for profile image 
from datetime import datetime, UTC
@app.context_processor
def inject_now():
    return {'now': int(datetime.now(UTC).timestamp())}