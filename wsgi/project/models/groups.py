# -*- coding: utf-8 -*-

from project.models.models import db

class Groups(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    alias_name = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    type = db.Column(db.Integer, nullable=False)
