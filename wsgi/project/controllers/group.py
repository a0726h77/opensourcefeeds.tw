# -*- coding: utf-8 -*-

from project import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
import datetime
import os
import glob

from project.models.models import db
from project.models.groups import Groups
from project.models.group_types import GroupTypes
from project.models.group_websites import GroupWebsites
from project.models.events import Events


@app.endpoint('group.page')
def page(group_id):
    group = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id, Groups.id == group_id).one()

    icon_list = list_icon_name()
    group_websites = GroupWebsites.query.filter(GroupWebsites.group_id == group_id).all()
    group_websites_has_icon = []
    group_websites_no_icon = []
    for group_website in group_websites:
        if group_website.name.lower().replace(' ', '') in icon_list:
            group_websites_has_icon.append(group_website)
        else:
            group_websites_no_icon.append(group_website)

    recent_events = Events.query.filter(Events.group_id == group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()

    past_events = Events.query.filter(Events.group_id == group_id, Events.start_datetime < datetime.datetime.now()).order_by(Events.start_datetime.desc()).limit(8)

    return render_template('group/page.html', group=group, group_websites_no_icon=group_websites_no_icon, group_websites_has_icon=group_websites_has_icon, recent_events=recent_events, past_events=past_events)


@app.endpoint('group.add')
def add():
    group = db.session.execute(Groups.__table__.insert({'name': '_'}))
    db.session.commit()

    return redirect(url_for('group.edit', group_id=group.lastrowid))


@app.endpoint('group.edit')
def edit(group_id):
    support_sites = ['Facebook', 'Flickr', 'Google+', 'Google Groups', 'KKTIX', 'Meetup', 'Twitter', 'YouTube']
    icon_list = list_icon_name()

    if request.method == 'POST':
        if 'url' in request.form:
            data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

            data['group_id'] = group_id

            if data['name'] not in support_sites:
                data['name'] = data['custom_name']

            del data['custom_name']

            website = db.session.execute(GroupWebsites.__table__.insert(data))
            db.session.commit()
        elif 'name' in request.form:
            rows_changed = Groups.query.filter(Groups.id == group_id).update(request.form)
            db.session.commit()

        return redirect(url_for('group.edit', group_id=group_id))
    else:
        group = Groups.query.filter(Groups.id == group_id).one()

        group_types = GroupTypes.query.all()

        group_websites = GroupWebsites.query.filter(GroupWebsites.group_id == group_id).all()
        group_websites_has_icon = []
        group_websites_no_icon = []
        for group_website in group_websites:
            if group_website.name.lower().replace(' ', '') in icon_list:
                group_websites_has_icon.append(group_website)
            else:
                group_websites_no_icon.append(group_website)

        return render_template('group/edit.html', group=group, group_types=group_types, group_websites_has_icon=group_websites_has_icon, group_websites_no_icon=group_websites_no_icon, support_sites=support_sites, icon_list=icon_list)


@app.endpoint('group.all_html')
def all_html():
    groups = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id).order_by(Groups.type, Groups.name).all()

    return render_template('group/list.html', groups=groups)


def list_icon_name():
    ICON_PATH = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../static/images/32x32')
    files = list_files(ICON_PATH, '*.png')
    icon_name = [f[:-4] for f in files]
    return icon_name


def list_files(path, file_filter='*'):
    os.chdir(path)
    files = glob.glob(file_filter)
    files.sort()
    return files


