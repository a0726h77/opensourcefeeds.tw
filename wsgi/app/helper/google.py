#!/usr/bin/env python
# encoding: utf-8

from app import app
from rauth.service import OAuth2Service
import ConfigParser
import os
from os.path import expanduser

if 'OPENSHIFT_DATA_DIR' in os.environ:
    config_file = os.environ['OPENSHIFT_DATA_DIR'] + '/.opensourcefeeds.cfg'
else:
    config_file = expanduser("~") + '/.opensourcefeeds.cfg'
config = ConfigParser.SafeConfigParser()
config.read(config_file)


google = OAuth2Service(name='google',
                         authorize_url='https://accounts.google.com/o/oauth2/auth',
                         access_token_url='https://accounts.google.com/o/oauth2/token',
                         client_id=config.get('GOOGLE', 'client_id'),
                         client_secret=config.get('GOOGLE', 'client_secret'),
                         base_url='https://www.googleapis.com/oauth2/v1/',
                         )
