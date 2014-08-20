# -*- coding: utf-8 -*-

from project import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack

from project.models.models import db
from project.models.groups import Groups
from project.models.group_types import GroupTypes


@app.endpoint('group.all_html')
def all_html():
    groups = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id).order_by(Groups.type, Groups.name).all()

    return render_template('group/list.html', groups=groups)
