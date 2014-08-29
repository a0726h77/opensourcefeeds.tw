# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug.contrib.atom import AtomFeed
import datetime

from app.models.models import db
from app.models.groups import Groups
from app.models.events import Events


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
