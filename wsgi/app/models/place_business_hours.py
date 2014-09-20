# -*- coding: utf-8 -*-

from app.models.models import db

class PlaceBusinessHours(db.Model):
    __tablename__ = 'place_business_hours'

    place_id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer, primary_key=True)
    from_time = db.Column(db.Time)
    till_time = db.Column(db.Time)
