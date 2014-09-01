# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
from pygeocoder import Geocoder

from app.models.models import db
from app.models.places import Places
from app.models.poi_types import POITypes
from app.models.place_tag import PlaceTag
from app.models.place_tags import PlaceTags


# TODO
# group by lat, lng
# caculate distance
@app.endpoint('place.cafe.index')
def cafe_index():
    poi_type = POITypes.query.filter(POITypes.name == 'Cafe').one()

    if request.method == 'POST':
        places = None

        if 'station' in request.form and request.form['station']:  # 臨近捷運站
            # places = Places.query.filter(Places.mrt == request.form['station'], Places.poi_type == poi_type.id).all()

            scale = 0.57
            Places.coords = classmethod(lambda s: (s.lat, s.lng))

            mrt = Places.query.filter(Places.id == request.form['station']).one()

            places = Places.query.filter(db.or_(calc_distance(Places.coords(), (mrt.lat, mrt.lng)) < scale, Places.mrt == request.form['station']), Places.poi_type == poi_type.id).order_by(calc_distance(Places.coords(), (mrt.lat, mrt.lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            places = Places.query.filter(db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/cafe_list.html', places=places)

    return ''


# TODO
# redirect to place page
@app.endpoint('place.cafe.add')
def cafe_add():
    if request.method == 'POST':
        poi_type = POITypes.query.filter(POITypes.name == 'Cafe').one()

        data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

        if 'address' in data:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                data['lat'] = coordinates[0]
                data['lng'] = coordinates[1]

        data['wireless'] = 1 if 'wireless' in data else 0
        data['electrical_plug'] = 1 if 'electrical_plug' in data else 0

        data['poi_type'] = poi_type.id

        place = db.session.execute(Places.__table__.insert(data))
        db.session.commit()

        return redirect(url_for('index'))
    else:
        ## mrt station list ##
        poi_type = POITypes.query.filter(POITypes.name == 'Station').one()

        stations = Places.query.filter(Places.poi_type == poi_type.id).order_by(Places.name).all()
        ## mrt station list ##

        return render_template('place/cafe_add.html', stations=stations)


@app.endpoint('place.hackerspace.index')
def hackerspace_index():
    poi_tag = PlaceTags.query.filter(PlaceTags.name == 'Hackerspace').one()

    if request.method == 'POST':
        places = None

        query_place_tag = PlaceTag.query.with_entities(PlaceTag.place_id).filter(PlaceTag.tag_id == poi_tag.id)

        if 'location' in request.form and request.form['location']:  # 北, 中, 南
            scale = 60  # 尚需校正
            Places.coords = classmethod(lambda s: (s.lat, s.lng))

            if request.form['location'] == 'n':
                lat, lng = 25.047923,121.51708000000008
            elif request.form['location'] == 'c':
                lat, lng = 24.13678, 120.68500799999993
            elif request.form['location'] == 's':
                lat, lng = 22.997144,120.21296600000005

            places = Places.query.filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            places = Places.query.filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/hackerspace_list.html', places=places)

    return ''


@app.endpoint('place.coworking_space.index')
def coworking_space_index():
    poi_tag = PlaceTags.query.filter(PlaceTags.name == 'Coworking Space').one()

    if request.method == 'POST':
        places = None

        query_place_tag = PlaceTag.query.with_entities(PlaceTag.place_id).filter(PlaceTag.tag_id == poi_tag.id)

        if 'location' in request.form and request.form['location']:  # 北, 中, 南
            scale = 60  # 尚需校正
            Places.coords = classmethod(lambda s: (s.lat, s.lng))

            if request.form['location'] == 'n':
                lat, lng = 25.047923,121.51708000000008
            elif request.form['location'] == 'c':
                lat, lng = 24.13678, 120.68500799999993
            elif request.form['location'] == 's':
                lat, lng = 22.997144,120.21296600000005

            places = Places.query.filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            places = Places.query.filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/coworking_space_list.html', places=places)

    return ''


def calc_distance(latlong1, latlong2):
    return db.func.sqrt(db.func.pow(69.1 * (latlong1[0] - latlong2[0]), 2)
                      + db.func.pow(53.0 * (latlong1[1] - latlong2[1]), 2))


def address_to_coordinates(address):
    try:
        results = Geocoder.geocode(address)

        return results[0].coordinates
    except:
        print 'address not found : %s' % address
        return None
