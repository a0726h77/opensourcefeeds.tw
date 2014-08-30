#!/usr/bin/env python
# encoding: utf-8

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
import json

from app.helper.google import google

from app.models.models import db
from app.models.users import Users


@app.endpoint('login.google')
def login():
    redirect_uri = url_for('authorized.google', _external=True)
    params = {'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'email'}
    return redirect(google.get_authorize_url(**params))


@app.endpoint('authorized.google')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized.google', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri, grant_type='authorization_code')

    oauth2_session = google.get_auth_session(data=data, decoder=json.loads)

    # get response
    json_path = 'https://www.googleapis.com/oauth2/v1/userinfo'
    session_json = oauth2_session.get(json_path).json()
    # session_json = dict((k, unicode(v).encode('utf-8')) for k, v in session_json.iteritems())

    # save user
    user = Users.query.filter(Users.email == session_json['email']).first()
    if not user:
        user_data = {}
        user_data['name'] = session_json['name']
        user_data['email'] = session_json['email']

        user = db.session.execute(Users.__table__.insert(user_data))
        db.session.commit()

        user = Users.query.filter(Users.email == session_json['email']).one()

    # set session
    session['user_id'] = user.id
    # session['user_name'] = session_json['given_name'].decode('utf-8') if session_json['given_name'] else session_json['name'].decode('utf-8')
    session['user_name'] = session_json['given_name'] if session_json['given_name'] else session_json['name']
    session['user_email'] = user.email

    return redirect(url_for('index'))
