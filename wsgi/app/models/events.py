# -*- coding: utf-8 -*-

from app.models.models import db

class Events(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    place = db.Column(db.Integer)
    people_count = db.Column(db.Integer)
    updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
