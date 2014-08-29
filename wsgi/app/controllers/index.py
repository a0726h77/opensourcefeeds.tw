# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory

from app.models.models import db
from app.models.groups import Groups
from app.models.group_types import GroupTypes


@app.endpoint('index')
def index():
    # return render_template('index.html')
    return redirect(url_for('group.all_html'))


@app.endpoint('robots.txt')
def serve_robots():
    return send_from_directory(app.static_folder, request.path[1:])
