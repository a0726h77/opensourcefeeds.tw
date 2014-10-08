# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
import datetime
import os
import glob
import re
import urllib2
import json

from app.models.models import db
from app.models.groups import Groups
from app.models.group_types import GroupTypes
from app.models.group_websites import GroupWebsites
from app.models.events import Events
from app.models.group_facebook_id import GroupFacebookID
from app.models.user_star_group import UserStarGroup
from app.models.search_cache import SearchCache


@app.endpoint('group.page')
def page(group_id):
    ## group info ##
    try:
        group = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id, Groups.id == group_id).one()
    except:
        return redirect(url_for('group.edit', group_id=group_id))
    ## group info ##

    ## recent and past events ##
    icon_list = list_icon_name()
    group_websites = GroupWebsites.query.filter(GroupWebsites.group_id == group_id).all()
    group_websites_has_icon = []
    group_websites_no_icon = []
    for group_website in group_websites:
        if group_website.name.lower().replace(' ', '') in icon_list:
            if group_website.name == 'IRC' and 'freenode' in group_website.url:
                group_websites_has_icon.append({'name': 'IRC', 'url': 'http://webchat.freenode.net/?channels=h4'})
            else:
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
        elif group_website.name == 'Plurk':
            feeds.append({'title': 'Plurk', 'url': '%s.xml' % group_website.url})
        elif group_website.name == 'Wikidot':
            feeds.append({'title': 'Wikidot', 'url': '%s/feed/site-changes.xml' % group_website.url})
        elif group_website.name == 'Google+':
            google_plus_id = get_google_plus_id(group_website.url)

            if google_plus_id:
                feeds.append({'title': 'Google+', 'url': 'https://gplus-to-rss.appspot.com/rss/%s' % google_plus_id})
        elif group_website.name == 'Twitter':
            username = get_twitter_username(group_website.url)

            if username:
                feeds.append({'title': 'Twitter', 'url': 'http://www.rssitfor.me/getrss?name=%s' % username})
        elif group_website.name == 'Blogger':
            feeds.append({'title': 'Blogger', 'url': '%s/feeds/posts/default' % group_website.url})
        elif group_website.name == 'SlideShare':
            slideshare_username = get_slideshare_username(group_website.url)

            if slideshare_username:
                feeds.append({'title': 'SlideShare', 'url': 'http://www.slideshare.net/rss/user/%s' % slideshare_username})
        elif group_website.name == 'YouTube':
            youtube_username = get_youtube_username(group_website.url)

            if youtube_username:
                feeds.append({'title': 'YouTube', 'url': 'https://gdata.youtube.com/feeds/api/users/%s/uploads' % youtube_username})
    ## rss feed link ##

    ## user star group ##
    star = None
    if 'user_id' in session:
        star = UserStarGroup.query.filter(UserStarGroup.user_id == session['user_id'], UserStarGroup.group_id == group_id).all()
    ## user star group ##

    return render_template('group/page.html', group=group, group_websites_no_icon=group_websites_no_icon, group_websites_has_icon=group_websites_has_icon, recent_events=recent_events, past_events=past_events, feeds=feeds, repos=repos, star=star)


@app.endpoint('group.add')
def add():
    group = db.session.execute(Groups.__table__.insert({'name': '_'}))
    db.session.commit()

    return redirect(url_for('group.edit', group_id=group.lastrowid))


@app.endpoint('group.edit')
def edit(group_id):
    if 'user_id' in session:
        support_sites = ['Accupass', 'Blogger', 'Facebook', 'Flickr', 'GitHub', 'Google+', 'Google Groups', 'Hackpad', 'KKTIX', 'Meetup', 'Plurk', 'Twitter', 'Ustream', 'Wikidot', 'YouTube', 'Peatix', 'Trello', 'Tumblr', 'IRC']
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
    else:
        return redirect(url_for('login'))


@app.endpoint('group.all_html')
def all_html():
    if 'user_id' in session:
        # 使用者關注的社群排在前面
        groups = db.session.query(Groups, GroupTypes, UserStarGroup).outerjoin(UserStarGroup, db.and_(Groups.id == UserStarGroup.group_id, UserStarGroup.user_id == session['user_id'])).filter(Groups.type == GroupTypes.id)

        # TODO
        # search location
        # search tags
        if request.method == 'POST':  # 搜尋相關社群
            groups = groups.filter(db.or_(Groups.name.like('%%%s%%' % request.form['search']), Groups.alias_name.like('%%%s%%' % request.form['search']), Groups.short_name.like('%%%s%%' % request.form['search'])))

        groups = groups.order_by(UserStarGroup.group_id.desc(), Groups.type, Groups.name).all()
    else:
        groups = db.session.query(Groups, GroupTypes).filter(Groups.type == GroupTypes.id)

        if request.method == 'POST':  # 搜尋相關社群
            groups = groups.filter(db.or_(Groups.name.like('%%%s%%' % request.form['search']), Groups.alias_name.like('%%%s%%' % request.form['search']), Groups.short_name.like('%%%s%%' % request.form['search'])))

        groups = groups.order_by(Groups.type, Groups.name).all()

    # save user search #
    if request.method == 'POST' and request.form['search']:
        search_cache = SearchCache.query.filter(SearchCache.text == request.form['search']).all()
        if not search_cache:
            db.session.execute(SearchCache.__table__.insert({'text': request.form['search']}))
            db.session.commit()
    # save user search #

    return render_template('group/list.html', groups=groups)


@app.endpoint('group.star')
def star(group_id):
    if 'user_id' in session:
        user_star_group = db.session.execute(UserStarGroup.__table__.insert({'user_id': session['user_id'], 'group_id': group_id}))
        db.session.commit()

        return ''
    else:
        abort(500)


@app.endpoint('group.unstar')
def unstar(group_id):
    if 'user_id' in session:
        UserStarGroup.query.filter(UserStarGroup.user_id == session['user_id'], UserStarGroup.group_id == group_id).delete()
        db.session.commit()

        return ''
    else:
        abort(500)


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

    m = re.search('https://github.com/([\w\-]+)[/]?', url)
    if m:
        return m.groups()[0]

def get_github_repos(username):
    url = 'https://api.github.com/users/%s/repos' % username

    connection = urllib2.urlopen(url)
    response = connection.read()

    return json.loads(response)


def get_slideshare_username(url):
    m = re.search('http://www.slideshare.net/([\w\.]+)[/]?', url)

    if m:
        return m.groups()[0]


def get_youtube_username(url):
    m = re.search('http[s]?://www.youtube.com/(user|channel)/([\w\.]+)[/]?', url)

    if m:
        return m.groups()[1]


def get_google_plus_id(url):
    # m = re.search('https://plus.google.com/(u/0/)?(communities/)?(\d+)', url)
    m = re.search('https://plus.google.com/(u/0/)?(\d+)', url)

    if m:
        # return m.groups()[2]
        return m.groups()[1]
