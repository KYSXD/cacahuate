from flask import Flask
from flask_coralillo import Coralillo
import os
import time

from lib.forms import bind_forms
from lib.models import bind_models

# The flask application
app = Flask(__name__)
app.config.from_object('settings')
app.config.from_envvar('PVM_SETTINGS', silent=False)

# Timezone
os.environ['TZ'] = app.config.get('TIMEZONE', 'UTC')
time.tzset()

# Bind the database
cora = Coralillo(app)
bind_forms(cora._engine)
bind_models(cora._engine)

# Views
import lib.views

# Error handlers
import lib.http.error_handlers
