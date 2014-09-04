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
    Rule('/event/json', endpoint='event.json'),
    Rule('/event/rss', endpoint='event.rss'),
    Rule('/event/calendar', endpoint='event.calendar'),
    Rule('/user/<user_id>/event/rss', endpoint='event.star_group_rss'),
    Rule('/place/<place_id>', endpoint='place.page'),
    Rule('/place/add', endpoint='place.add'),
    Rule('/place/edit/<place_id>', endpoint='place.edit'),
    Rule('/place/search', endpoint='place.search'),
    Rule('/place/cafe', endpoint='place.cafe.index'),
    Rule('/place/add/cafe', endpoint='place.cafe.add'),
    Rule('/place/hackerspace', endpoint='place.hackerspace.index'),
    Rule('/place/add/hackerspace', endpoint='place.hackerspace.add'),
    Rule('/place/coworking_space', endpoint='place.coworking_space.index'),
    Rule('/place/add/coworking_space', endpoint='place.coworking_space.add'),
    Rule('/place/<place_id>/star', endpoint='place.star'),
    Rule('/place/<place_id>/unstar', endpoint='place.unstar'),
    Rule('/robots.txt', endpoint='robots.txt'),
    Rule('/google/login', endpoint='login.google'),
    Rule('/google/authorized', endpoint='authorized.google'),
    Rule('/facebook/login', endpoint='login.facebook'),
    Rule('/facebook/authorized', endpoint='authorized.facebook'),
    Rule('/github/login', endpoint='login.github'),
    Rule('/github/authorized', endpoint='authorized.github'),
    Rule('/login', endpoint='login'),
    Rule('/logout', endpoint='logout'),
}
