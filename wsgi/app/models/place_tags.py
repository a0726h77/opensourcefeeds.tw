# -*- coding: utf-8 -*-

from app.models.models import db

class PlaceTags(db.Model):
    __tablename__ = 'place_tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
