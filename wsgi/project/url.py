#!/usr/bin/env python
# encoding: utf-8

from werkzeug.routing import Rule

urlpatterns = {
    Rule('/', endpoint='index'),
    Rule('/group/html', endpoint='group.all_html'),
    Rule('/event/rss', endpoint='event.rss'),
}
