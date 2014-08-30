# -*- coding: utf-8 -*-

from app.models.models import db

class UserStarGroup(db.Model):
    __tablename__ = 'user_star_group'

    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, primary_key=True)
