# -*- coding: utf-8 -*-

from app.models.models import db

class POITypes(db.Model):
    __tablename__ = 'poi_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
