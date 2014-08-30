#!/usr/bin/env python
# encoding: utf-8

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
import json

from app.helper.facebook import facebook

from app.models.models import db
from app.models.users import Users


@app.endpoint('login.facebook')
def login():
    redirect_uri = url_for('authorized.facebook', _external=True)
    params = {'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'email'}
    return redirect(facebook.get_authorize_url(**params))


@app.endpoint('authorized.facebook')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized.facebook', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    oauth2_session = facebook.get_auth_session(data=data)

    # get response
    json_path = '/me'
    session_json = oauth2_session.get(json_path).json()

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
    session['user_name'] = session_json['name']
    session['user_email'] = user.email

    return redirect(url_for('index'))
