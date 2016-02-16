from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.extensions import db


class Hint(db.Model):
    __tablename__ = 'hint'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'hint',
        'polymorphic_on': type
    }


class ScaleHint(Hint):
    __tablename__ = 'hint_scale'
    id = Column(Integer, ForeignKey('hint.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'hintScale'}


class NumericHint(Hint):
    __tablename__ = 'hint_numeric'
    id = Column(Integer, ForeignKey('hint.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'hintNumeric'}