# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask
app = Flask('app')
app.debug = True

# import controllers
from app.controllers import *

# import model
from models.models import db


#### initial logger ####
# import logging
# from logging.handlers import RotatingFileHandler
# import os
#
# LOG_PATH = '/'.join((os.path.dirname(os.path.realpath(__file__)), 'log'))
# if not os.path.exists(LOG_PATH):
#     os.makedirs(LOG_PATH)
#
# handler = RotatingFileHandler(LOG_PATH + '/debug.log', maxBytes=10000, backupCount=1)
# handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
# handler.setLevel(logging.INFO)
# app.logger.addHandler(handler)
#### initial logger ####


#### initial sesion ####
from datetime import timedelta
app.config['SECRET_KEY'] = 'secret'
app.permanent_session_lifetime = timedelta(seconds=60*60*10)  # session expire time
#### initial sesion ####


#### initial database ####
import os
from os.path import expanduser

## web config ##
app.config.from_pyfile(expanduser("~") + '/.opensourcefeeds_web.cfg')
## web config ##

## Remote database config
import ConfigParser
if 'OPENSHIFT_DATA_DIR' in os.environ:
    config_file = os.environ['OPENSHIFT_DATA_DIR'] + '/.opensourcefeeds.cfg'
else:
    config_file = expanduser("~") + '/.opensourcefeeds.cfg'
config = ConfigParser.SafeConfigParser()
config.read(config_file)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (config.get('DATABASE', 'username'), config.get('DATABASE', 'password'), config.get('DATABASE', 'host'), config.get('DATABASE', 'database'))

# # OpenShift local database config
# app.config.from_pyfile('config/database.cfg')

db.init_app(app)

# # initial database
# with app.app_context():
#     # db.drop_all()
#     db.create_all()
#### initial database ####


#### router ####
from url import urlpatterns

for rule in urlpatterns:
    app.url_map.add(rule)
#### router ####
