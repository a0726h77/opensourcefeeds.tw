# -*- coding: utf-8 -*-

from project import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack

from project.models.models import db
from project.models.groups import Groups
from project.models.group_types import GroupTypes
from project.models.group_websites import GroupWebsites


@app.endpoint('group.page')
def page(group_id):
    group = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id, Groups.id == group_id).one()

    icon_list = ['facebook', 'flickr', 'googleplus', 'google+', 'kktix', 'meetup', 'twitter', 'youtube']
    group_websites = GroupWebsites.query.filter(GroupWebsites.group_id == group_id).all()
    group_websites_has_icon = []
    group_websites_no_icon = []
    for group_website in group_websites:
        if group_website.name.lower() in icon_list:
            group_websites_has_icon.append(group_website)
        else:
            group_websites_no_icon.append(group_website)

    return render_template('group/page.html', group=group, group_websites_no_icon=group_websites_no_icon, group_websites_has_icon=group_websites_has_icon)


@app.endpoint('group.all_html')
def all_html():
    groups = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id).order_by(Groups.type, Groups.name).all()

    return render_template('group/list.html', groups=groups)
