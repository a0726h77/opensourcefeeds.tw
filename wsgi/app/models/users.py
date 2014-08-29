# -*- coding: utf-8 -*-

from app.models.models import db

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
