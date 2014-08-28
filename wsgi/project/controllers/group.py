# -*- coding: utf-8 -*-

from project import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
import datetime
import os
import glob
import re
import urllib2
import json

from project.models.models import db
from project.models.groups import Groups
from project.models.group_types import GroupTypes
from project.models.group_websites import GroupWebsites
from project.models.events import Events
from project.models.group_facebook_id import GroupFacebookID


@app.endpoint('group.page')
def page(group_id):
    ## group info ##
    group = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id, Groups.id == group_id).one()
    ## group info ##

    ## recent and past events ##
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

    past_events = Events.query.filter(Events.group_id == group_id, db.or_(Events.start_datetime < datetime.datetime.now(), Events.start_datetime == None)).order_by(Events.start_datetime.desc()).limit(8)
    ## recent and past events ##


    ## Github repo ##
    repos = []
    for group_website in group_websites:
        if group_website.name == 'GitHub':
            username = get_github_username(group_website.url)
            if username:
                repos = get_github_repos(username)
    ## Github repo ##

    ## rss feed link ##
    feeds = []
    for group_website in group_websites:
        if group_website.name == 'Facebook':
            facebook_id = get_facebook_id(group_website.url)

            if facebook_id:
                feeds.append({'title': 'Facebook', 'url': 'http://www.wallflux.com/atom/%s' % facebook_id})
        elif group_website.name == 'Google Groups':
            google_groups_url_name = get_google_groups_url_name(group_website.url)

            if google_groups_url_name:
                feeds.append({'title': 'Google Groups', 'url': 'https://groups.google.com/group/%s/feed/rss_v2_0_msgs.xml' % google_groups_url_name})
        elif group_website.name == 'Tumblr':
            feeds.append({'title': 'Tumblr', 'url': '%s/rss' % group_website.url})
        elif group_website.name == 'Twitter':
            username = get_twitter_username(group_website.url)

            if username:
                feeds.append({'title': 'Twitter', 'url': 'http://www.rssitfor.me/getrss?name=%s' % username})
    ## rss feed link ##

    return render_template('group/page.html', group=group, group_websites_no_icon=group_websites_no_icon, group_websites_has_icon=group_websites_has_icon, recent_events=recent_events, past_events=past_events, feeds=feeds, repos=repos)


@app.endpoint('group.add')
def add():
    group = db.session.execute(Groups.__table__.insert({'name': '_'}))
    db.session.commit()

    return redirect(url_for('group.edit', group_id=group.lastrowid))


@app.endpoint('group.edit')
def edit(group_id):
    support_sites = ['Accupass', 'Blogger', 'Facebook', 'Flickr', 'GitHub', 'Google+', 'Google Groups', 'Hackpad', 'KKTIX', 'Meetup', 'Plurk', 'Twitter', 'Ustream', 'Wikidot', 'YouTube', 'Peatix', 'Trello', 'Tumblr']
    support_sites.sort()
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


def get_facebook_id(url):
    m = re.match('https://www.facebook.com/groups/(.*)/', url)

    if not m:
        m = re.search('https://www.facebook.com/([\w\.]+)[/]?', url)

    facebook_id = None
    if m:
        if m and re.search('([a-zA-Z\.]+)', m.groups()[0]):
            facebook_id = GroupFacebookID.query.filter(GroupFacebookID.group_urlname == m.groups()[0]).first()
            if facebook_id:
                facebook_id = facebook_id.facebook_id
        else:
            facebook_id = m.groups()[0]

    return facebook_id


def get_google_groups_url_name(url):
    m = re.search('#!forum\/(.*)', url)

    if m:
        return m.groups()[0]


def get_twitter_username(url):
    m = re.search('https://twitter.com/([\w\.]+)[/]?', url)

    if m:
        return m.groups()[0]


def get_github_username(url):
    m = re.match('https://github.com/orgs/([\w-]+)[/]?', url)
    if m:
        return m.groups()[0]

    m = re.search('https://github.com/([\w\.]+)[/]?', url)
    if m:
        return m.groups()[0]

def get_github_repos(username):
    url = 'https://api.github.com/users/%s/repos' % username

    connection = urllib2.urlopen(url)
    response = connection.read()

    return json.loads(response)
