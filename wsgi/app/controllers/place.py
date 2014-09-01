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
    poi_type = POITypes.query.filter(POITypes.name == 'Cafe').one()

    if request.method == 'POST':
        places = None

        if 'station' in request.form and request.form['station']:  # 臨近捷運站
            places = Places.query.filter(Places.mrt == request.form['station'], Places.poi_type == poi_type.id).all()
        elif 'name' in request.form:  # 關鍵字查詢
            places = Places.query.filter(db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/cafe_list.html', places=places)

    return ''
