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


github = OAuth2Service(name='github',
                         authorize_url='https://github.com/login/oauth/authorize',
                         access_token_url='https://github.com/login/oauth/access_token',
                         client_id=config.get('GITHUB', 'client_id'),
                         client_secret=config.get('GITHUB', 'client_secret'),
                         base_url='https://api.github.com/',
                         )
