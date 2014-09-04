# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
import datetime

from app.models.models import db
from app.models.groups import Groups
from app.models.group_types import GroupTypes
from app.models.events import Events
from app.models.user_star_group import UserStarGroup
from app.models.places import Places
from app.models.poi_types import POITypes


@app.endpoint('index')
def index():
    ## user start groups ##
    star_groups = None
    if 'user_id' in session:
        star_groups = UserStarGroup.query.filter(UserStarGroup.user_id == session['user_id']).all()
        star_groups = [star_group.group_id for star_group in star_groups]
    ## user start groups ##

    ## mrt station list ##
    poi_type = POITypes.query.filter(POITypes.name == 'Station').one()

    stations = Places.query.filter(Places.poi_type == poi_type.id).order_by(Places.name).all()
    ## mrt station list ##

    return render_template('index.html', recent_events=recent_events, star_groups=star_groups, stations=stations)
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
