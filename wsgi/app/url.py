#!/usr/bin/env python
# encoding: utf-8

from werkzeug.routing import Rule

urlpatterns = {
    Rule('/', endpoint='index'),
    Rule('/group/<group_id>', endpoint='group.page'),
    Rule('/group/add', endpoint='group.add'),
    Rule('/group/edit/<group_id>', endpoint='group.edit'),
    Rule('/group/html', endpoint='group.all_html'),
    Rule('/event/rss', endpoint='event.rss'),
    Rule('/robots.txt', endpoint='robots.txt'),
    Rule('/google/login', endpoint='login.google'),
    Rule('/google/authorized', endpoint='authorized.google'),
    Rule('/login', endpoint='login'),
    Rule('/logout', endpoint='logout'),
}
