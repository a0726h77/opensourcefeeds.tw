# -*- coding: utf-8 -*-

from app.models.models import db

class Places(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    wireless = db.Column(db.Integer)
    electrical_plug = db.Column(db.Integer)
    average_charge = db.Column(db.String(255))
    seats = db.Column(db.Integer)
    mrt = db.Column(db.Integer)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float(Precision=64))
    lng = db.Column(db.Float(Precision=64))
    phone = db.Column(db.String(255))
    active = db.Column(db.Integer, default=1)
    url = db.Column(db.String(512))
    poi_type = db.Column(db.Integer)
