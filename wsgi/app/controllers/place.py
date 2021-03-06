# -*- coding: utf-8 -*-

from app import app
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, send_from_directory
from pygeocoder import Geocoder
import json
import datetime

from app.models.models import db
from app.models.places import Places
from app.models.poi_types import POITypes
from app.models.place_tag import PlaceTag
from app.models.place_tags import PlaceTags
from app.models.place_business_hours import PlaceBusinessHours
from app.models.events import Events
from app.models.user_star_place import UserStarPlace


@app.endpoint('place.search')
def search():
    if request.method == 'POST':
        places = None

        if 'address' in request.form:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                ## 搜尋現有的場地人數 ##
                query_place = Places.query.with_entities(Places.id)

                if 'min_seats' in request.form and request.form['min_seats']:
                    query_place = query_place.filter(Places.seats >= request.form['min_seats'])

                if 'max_seats' in request.form and request.form['max_seats']:
                    query_place = query_place.filter(Places.seats <= request.form['max_seats'])
                ## 搜尋現有的場地人數 ##

                ## 搜尋辦過活動的場地有沒有適合的人數 ##
                query_event_place = Events.query.with_entities(Events.place)

                if 'min_seats' in request.form and request.form['min_seats']:
                    query_event_place = query_event_place.filter(Events.people_count >= request.form['min_seats'])

                if 'max_seats' in request.form and request.form['max_seats']:
                    query_event_place = query_event_place.filter(Events.people_count <= request.form['max_seats'])
                ## 搜尋辦過活動的場地有沒有適合的人數 ##

                scale = 20
                Places.coords = classmethod(lambda s: (s.lat, s.lng))

                if 'user_id' in session:
                    places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(db.or_(calc_distance(Places.coords(), (coordinates[0], coordinates[1])) < scale))
                    places = places.filter(db.or_(Places.id.in_(query_place), Places.id.in_(query_event_place))).order_by(calc_distance(Places.coords(), (coordinates[0], coordinates[1]))).all()
                else:
                    places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(db.or_(calc_distance(Places.coords(), (coordinates[0], coordinates[1])) < scale))
                    places = places.filter(db.or_(Places.id.in_(query_place), Places.id.in_(query_event_place))).order_by(calc_distance(Places.coords(), (coordinates[0], coordinates[1]))).all()

        return render_template('place/search.html', places=places)
    else:
        return ''


# TODO
# redirect to place page
@app.endpoint('place.add')
def add():
    if request.method == 'POST':
        data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

        if 'address' in data:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                data['lat'] = coordinates[0]
                data['lng'] = coordinates[1]

        data['wireless'] = 1 if 'wireless' in data else 0
        data['electrical_plug'] = 1 if 'electrical_plug' in data else 0

        place_tag = []
        if 'place_tag' in data:
            place_tag = [int(place_tag) for place_tag in request.form.getlist("place_tag")]
            del data['place_tag']

        place = db.session.execute(Places.__table__.insert(data))
        db.session.commit()

        ## 新增 place tag ##
        for tag_id in place_tag:
            db.session.execute(PlaceTag.__table__.insert({'place_id': place.lastrowid, 'tag_id': tag_id}))

        db.session.commit()
        ## 新增/刪除 place tag ##

        if place:
            return redirect(url_for('place.page', place_id=place.lastrowid))
        else:
            return redirect(url_for('index'))
    else:
        ## mrt station list ##
        poi_type = POITypes.query.filter(POITypes.name == 'Station').one()

        stations = Places.query.filter(Places.poi_type == poi_type.id).order_by(Places.name).all()
        ## mrt station list ##

        ## place tags ##
        place_tags = PlaceTags.query.all()
        ## place tags ##

        return render_template('place/add.html', stations=stations, place_tags=place_tags)


# TODO
# redirect to place page
@app.endpoint('place.edit')
def edit(place_id):
    if request.method == 'POST':
        data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

        if 'address' in data:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                data['lat'] = coordinates[0]
                data['lng'] = coordinates[1]

        data['wireless'] = 1 if 'wireless' in data else 0
        data['electrical_plug'] = 1 if 'electrical_plug' in data else 0

        place_tag = []
        if 'place_tag' in data:
            place_tag = [int(place_tag) for place_tag in request.form.getlist("place_tag")]
            del data['place_tag']

        place = Places.query.filter(Places.id == place_id).update(data)
        db.session.commit()

        ## 新增/刪除 place tag ##
        place_has_tag = PlaceTag.query.filter(PlaceTag.place_id == place_id).all()
        place_has_tag = [tag.tag_id for tag in place_has_tag]

        # 新增加的
        added = set(place_tag) - set(place_has_tag)
        for tag_id in added:
            db.session.execute(PlaceTag.__table__.insert({'place_id': place_id, 'tag_id': tag_id}))

        # 刪除的
        removed = set(place_has_tag) - set(place_tag)
        for tag_id in removed:
            PlaceTag.query.filter(PlaceTag.place_id == place_id, PlaceTag.tag_id == tag_id).delete()

        db.session.commit()
        ## 新增/刪除 place tag ##

        return redirect(url_for('place.page', place_id=place_id))
    else:
        place = Places.query.filter(Places.id == place_id).one()

        ## mrt station list ##
        poi_type = POITypes.query.filter(POITypes.name == 'Station').one()

        stations = Places.query.filter(Places.poi_type == poi_type.id).order_by(Places.name).all()
        ## mrt station list ##

        ## place in tags ##
        place_has_tag = PlaceTag.query.filter(PlaceTag.place_id == place_id).all()
        place_has_tag = [tag.tag_id for tag in place_has_tag]
        ## place in tags ##

        ## place tags ##
        place_tags = PlaceTags.query.all()
        ## place tags ##

        ## poi types ##
        poi_types = POITypes.query.all()
        ## poi types ##

        ## business hours  ##
        business_hours = PlaceBusinessHours.query.filter(PlaceBusinessHours.place_id == place_id).order_by(PlaceBusinessHours.weekday).all()

        business_hours_json = []
        if business_hours:
            for business_hour in business_hours:
                _ = {}
                if business_hour.from_time and business_hour.till_time:
                    _['isActive'] = True
                    _['timeFrom'] = business_hour.from_time.strftime("%H:%M")
                    _['timeTill'] = business_hour.till_time.strftime("%H:%M")
                else:
                    _['isActive'] = False
                    _['timeFrom'] = None
                    _['timeTill'] = None

                business_hours_json.append(_)
        else:
            for business_hour in range(0, 7):
                _ = {}
                _['isActive'] = False
                _['timeFrom'] = None
                _['timeTill'] = None
                business_hours_json.append(_)
        ## business hours  ##

        return render_template('place/edit.html', place=place, stations=stations, poi_types=poi_types, place_tags=place_tags, place_has_tag=place_has_tag, business_hours_json=business_hours_json)


@app.endpoint('place.page')
def page(place_id):
    place = Places.query.filter(Places.id == place_id).one()

    ## near station ##
    station = None
    if place.mrt:
        station = Places.query.filter(Places.id == place.mrt).first()
    ## near station ##

    ## user star place ##
    star = None
    if 'user_id' in session:
        star = UserStarPlace.query.filter(UserStarPlace.user_id == session['user_id'], UserStarPlace.place_id == place_id).all()
    ## user star place ##

    ## business_hours ##
    business_hours = PlaceBusinessHours.query.filter(PlaceBusinessHours.place_id == place_id).order_by(PlaceBusinessHours.weekday).all()

    weekday = datetime.datetime.today().weekday() + 1
    ## business_hours ##

    return render_template('place/page.html', place=place, station=station, star=star, business_hours=business_hours, weekday=weekday)


# TODO
# group by lat, lng
# caculate distance
@app.endpoint('place.cafe.index')
def cafe_index():
    poi_type = POITypes.query.filter(POITypes.name == 'Cafe').one()

    places = []

    scale = 0.57
    Places.coords = classmethod(lambda s: (s.lat, s.lng))

    if request.method == 'POST':
        weekday = datetime.datetime.today().weekday() + 1

        if 'station' in request.form and request.form['station']:  # 臨近捷運站
            # places = Places.query.filter(Places.mrt == request.form['station'], Places.poi_type == poi_type.id).all()

            mrt = Places.query.filter(Places.id == request.form['station']).one()

            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes, PlaceBusinessHours).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).outerjoin(PlaceBusinessHours, db.and_(PlaceBusinessHours.place_id == Places.id, PlaceBusinessHours.weekday == weekday)).filter(db.or_(calc_distance(Places.coords(), (mrt.lat, mrt.lng)) < scale, Places.mrt == request.form['station']), Places.poi_type == poi_type.id).order_by(calc_distance(Places.coords(), (mrt.lat, mrt.lng))).all()
            else:
                places = db.session.query(Places, POITypes, PlaceBusinessHours).outerjoin(POITypes, Places.poi_type == POITypes.id).outerjoin(PlaceBusinessHours, db.and_(PlaceBusinessHours.place_id == Places.id, PlaceBusinessHours.weekday == weekday)).filter(db.or_(calc_distance(Places.coords(), (mrt.lat, mrt.lng)) < scale, Places.mrt == request.form['station']), Places.poi_type == poi_type.id).order_by(calc_distance(Places.coords(), (mrt.lat, mrt.lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes, PlaceBusinessHours).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).outerjoin(PlaceBusinessHours, db.and_(PlaceBusinessHours.place_id == Places.id, PlaceBusinessHours.weekday == weekday)).filter(db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()
            else:
                places = db.session.query(Places, POITypes, PlaceBusinessHours).outerjoin(POITypes, Places.poi_type == POITypes.id).outerjoin(PlaceBusinessHours, db.and_(PlaceBusinessHours.place_id == Places.id, PlaceBusinessHours.weekday == weekday)).filter(db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/cafe_list.html', places=places)
    else:
        if 'lat' in request.args and 'lng' in request.args:
            lat = request.args['lat']
            lng = request.args['lng']
            print lat
            print lng
            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(db.or_(calc_distance(Places.coords(), (lat, lng)) < scale), Places.poi_type == poi_type.id).order_by(calc_distance(Places.coords(), (lat, lng))).all()
            else:
                places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(db.or_(calc_distance(Places.coords(), (lat, lng)) < scale), Places.poi_type == poi_type.id).order_by(calc_distance(Places.coords(), (lat, lng))).all()

        return render_template('place/cafe_list.html', places=places)


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

        return redirect(url_for('place.page', place_id=place.lastrowid))
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

            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
            else:
                places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()
            else:
                places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/hackerspace_list.html', places=places)

    return ''


# TODO
# redirect to place page
@app.endpoint('place.hackerspace.add')
def hackerspace_add():
    if request.method == 'POST':
        place_tag = PlaceTags.query.filter(PlaceTags.name == 'Hackerspace').one()

        data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

        if 'address' in data:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                data['lat'] = coordinates[0]
                data['lng'] = coordinates[1]

        place = db.session.execute(Places.__table__.insert(data))
        db.session.commit()

        db.session.execute(PlaceTag.__table__.insert({'place_id': place.lastrowid, 'tag_id': place_tag.id}))
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template('place/hackerspace_add.html')


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

            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
            else:
                places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), calc_distance(Places.coords(), (lat, lng)) < scale).order_by(calc_distance(Places.coords(), (lat, lng))).all()
        elif 'name' in request.form:  # 關鍵字查詢
            if 'user_id' in session:
                places = db.session.query(Places, UserStarPlace, POITypes).outerjoin(UserStarPlace, db.and_(Places.id == UserStarPlace.place_id, UserStarPlace.user_id == session['user_id'])).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()
            else:
                places = db.session.query(Places, POITypes).outerjoin(POITypes, Places.poi_type == POITypes.id).filter(Places.id.in_(query_place_tag), db.or_(Places.name.like("%%%s%%" % request.form['name']), Places.address.like("%%%s%%" % request.form['name']))).all()

        return render_template('place/coworking_space_list.html', places=places)

    return ''


# TODO
# redirect to place page
@app.endpoint('place.coworking_space.add')
def coworking_space_add():
    if request.method == 'POST':
        place_tag = PlaceTags.query.filter(PlaceTags.name == 'Coworking Space').one()

        data = dict([[k, v] for k, v in request.form.items()])  # 將 form 轉爲可新增資料的變數

        if 'address' in data:
            coordinates = address_to_coordinates(request.form['address'])

            if coordinates:
                data['lat'] = coordinates[0]
                data['lng'] = coordinates[1]

        place = db.session.execute(Places.__table__.insert(data))
        db.session.commit()

        db.session.execute(PlaceTag.__table__.insert({'place_id': place.lastrowid, 'tag_id': place_tag.id}))
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return render_template('place/coworking_space_add.html')


@app.endpoint('place.star')
def star(place_id):
    if 'user_id' in session:
        user_star_place = db.session.execute(UserStarPlace.__table__.insert({'user_id': session['user_id'], 'place_id': place_id}))
        db.session.commit()

        return ''
    else:
        abort(500)


@app.endpoint('place.unstar')
def unstar(place_id):
    if 'user_id' in session:
        UserStarPlace.query.filter(UserStarPlace.user_id == session['user_id'], UserStarPlace.place_id == place_id).delete()
        db.session.commit()

        return ''
    else:
        abort(500)


@app.endpoint('place.business_hours_save')
def business_hours_save(place_id):
    if request.method == 'POST':
        operation_time = json.loads(request.form['operation_time'])

        weekday = 1
        for time in operation_time:
            data = {}
            data['place_id'] = place_id
            data['weekday'] = weekday
            if time['isActive']:
                data['from_time'] = time['timeFrom']
                data['till_time'] = time['timeTill']
            else:
                data['from_time'] = '00:00:00'
                data['till_time'] = '00:00:00'

            place_business_hour = PlaceBusinessHours.query.filter(PlaceBusinessHours.place_id == place_id, PlaceBusinessHours.weekday == weekday).first()

            if place_business_hour:  # update
                PlaceBusinessHours.query.filter(PlaceBusinessHours.place_id == place_id, PlaceBusinessHours.weekday == weekday).update(data)
            else:  # add
                db.session.execute(PlaceBusinessHours.__table__.insert(data))

            weekday = weekday + 1

        db.session.commit()

        return ''


def calc_distance(latlong1, latlong2):
    return db.func.sqrt(db.func.pow(69.1 * (latlong1[0] - latlong2[0]), 2)
                      + db.func.pow(53.0 * (latlong1[1] - latlong2[1]), 2))


def address_to_coordinates(address):
    try:
        results = Geocoder.geocode(address)

        return results[0].coordinates
    except:
        # print 'address not found : %s' % address
        return None
