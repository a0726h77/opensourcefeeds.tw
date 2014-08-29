# -*- coding: utf-8 -*-

from app.models.models import db

class GroupWebsites(db.Model):
    __tablename__ = 'group_websites'

    group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), primary_key=True)
