#!/usr/bin/env python
# encoding: utf-8

from werkzeug.routing import Rule

urlpatterns = {
    Rule('/', endpoint='index'),
    Rule('/group/<group_id>', endpoint='group.page'),
    Rule('/group/add', endpoint='group.add'),
    Rule('/group/edit/<group_id>', endpoint='group.edit'),
    Rule('/group/html', endpoint='group.all_html'),
    Rule('/group/<group_id>/star', endpoint='group.star'),
    Rule('/group/<group_id>/unstar', endpoint='group.unstar'),
    Rule('/event/rss', endpoint='event.rss'),
    Rule('/user/<user_id>/event/rss', endpoint='event.star_group_rss'),
    Rule('/robots.txt', endpoint='robots.txt'),
    Rule('/google/login', endpoint='login.google'),
    Rule('/google/authorized', endpoint='authorized.google'),
    Rule('/login', endpoint='login'),
    Rule('/logout', endpoint='logout'),
}
