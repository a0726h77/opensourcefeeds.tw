# -*- coding: utf-8 -*-

from app.models.models import db

class GroupTypes(db.Model):
    __tablename__ = 'group_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(255), nullable=False)
