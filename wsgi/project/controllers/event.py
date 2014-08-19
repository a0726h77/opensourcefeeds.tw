# -*- coding: utf-8 -*-

from project import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug.contrib.atom import AtomFeed
import datetime

from project.models.models import db
from project.models.events import Events


@app.endpoint('event.rss')
def rss():
    feed = AtomFeed('Recent Events', feed_url=request.url, url=request.url_root)
    # TODO
    # query end_datetime > today
    articles = Events.query.filter(Events.start_datetime > datetime.datetime.now()).order_by(Events.start_datetime).all()
    for article in articles:
        feed.add(article.name, unicode(article.name),
                 content_type='html',
                 url=article.url,
                 updated=article.start_datetime)
    return feed.get_response()
