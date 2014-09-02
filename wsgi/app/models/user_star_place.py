# -*- coding: utf-8 -*-

from app.models.models import db

class UserStarPlace(db.Model):
    __tablename__ = 'user_star_place'

    user_id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, primary_key=True)
