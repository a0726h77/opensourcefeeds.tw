# -*- coding: utf-8 -*-

from app.models.models import db

class PlacesTag(db.Model):
    __tablename__ = 'place_tag'

    place_id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, primary_key=True)
