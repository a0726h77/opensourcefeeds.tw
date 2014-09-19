# -*- coding: utf-8 -*-

from app.models.models import db

class SearchCache(db.Model):
    __tablename__ = 'search_cache'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Integer, default=0)
