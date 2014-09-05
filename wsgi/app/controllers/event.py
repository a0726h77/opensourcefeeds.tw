# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, Response
from werkzeug.contrib.atom import AtomFeed
import datetime
import json

from app.models.models import db
from app.models.groups import Groups
from app.models.events import Events
from app.models.user_star_group import UserStarGroup


@app.endpoint('event.index')
def index():
    recent_events = db.session.query(Groups, Events).filter(Groups.id == Events.group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()

    star_groups = None
    if 'user_id' in session:
        star_groups = UserStarGroup.query.filter(UserStarGroup.user_id == session['user_id']).all()
        star_groups = [group.group_id for group in star_groups]

    return render_template('event/index.html', recent_events=recent_events, star_groups=star_groups)


@app.endpoint('event.json')
def recent_event_json():
    events = db.session.query(Groups, Events).filter(Groups.id == Events.group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()

    results = []
    for event in events:
        _ = {}
        _['title'] = event.Events.name
        _['url'] = event.Events.url

        if event.Events.start_datetime:
            _['start'] = event.Events.start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        if event.Events.end_datetime:
            _['end'] = event.Events.end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

        results.append(_)

    return Response(json.dumps(results), mimetype='application/json')


@app.endpoint('event.rss')
def rss():
    feed = AtomFeed('Recent Events', feed_url=request.url, url=request.url_root)
    # TODO
    # query end_datetime > today
    articles = db.session.query(Groups, Events).filter(Groups.id == Events.group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()
    for article in articles:
        feed.add('%s [%s] %s' % (article.Events.start_datetime.strftime("%m/%d"), article.Groups.name, article.Events.name), unicode(article.Events.name),
                 content_type='html',
                 url=article.Events.url,
                 updated=article.Events.start_datetime - datetime.timedelta(hours=8))
    return feed.get_response()


@app.endpoint('event.star_group_rss')
def start_group_rss(user_id):
    feed = AtomFeed('Recent Events', feed_url=request.url, url=request.url_root)
    # TODO
    # query end_datetime > today
    query_user_star_group = UserStarGroup.query.with_entities(UserStarGroup.group_id).filter(UserStarGroup.user_id == user_id)
    articles = db.session.query(Groups, Events).filter(Groups.id.in_(query_user_star_group), Groups.id == Events.group_id, Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()
    for article in articles:
        feed.add('%s [%s] %s' % (article.Events.start_datetime.strftime("%m/%d"), article.Groups.name, article.Events.name), unicode(article.Events.name),
                 content_type='html',
                 url=article.Events.url,
                 updated=article.Events.start_datetime - datetime.timedelta(hours=8))
    return feed.get_response()


@app.endpoint('event.calendar')
def calendar():
    return render_template('event/calendar.html')
