# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
import datetime

from app.models.models import db
from app.models.groups import Groups
from app.models.group_types import GroupTypes
from app.models.events import Events


@app.endpoint('index')
def index():
    recent_events = db.session.query(Groups, Events).filter(Groups.id == Events.group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()

    return render_template('index.html', recent_events=recent_events)
    # return redirect(url_for('group.all_html'))


@app.endpoint('login')
def login():
    return render_template('login.html')


@app.endpoint('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.endpoint('robots.txt')
def serve_robots():
    return send_from_directory(app.static_folder, request.path[1:])
