from flask import Flask

DB_URI = 'mysql://game:game@localhost/info'
DEBUG = True
SECRET_KEY = 'foobarbaz'

app = Flask(__name__)
app.config.from_object(__name__)

import login_example.views