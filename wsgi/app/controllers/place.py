# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory

from app.models.models import db
from app.models.places import Places
from app.models.poi_types import POITypes


# TODO
# group by lat, lng
# caculate distance
@app.endpoint('place.cafe.index')
def cafe_index():
    if request.method == 'POST':
        if 'station' in request.form and request.form['station']:
            places = Places.query.filter(Places.mrt == request.form['station']).all()

            return render_template('place/cafe_list.html', places=places)

        if 'name' in request.form:
            poi_type = POITypes.query.filter(POITypes.name == 'Cafe').one()

            places = Places.query.filter(db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name'])), Places.poi_type == poi_type.id).all()

            return render_template('place/cafe_list.html', places=places)

    return ''
