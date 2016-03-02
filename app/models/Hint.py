from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.engine.convert import format_quantity, convert, format_value
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


class TextHint(Hint):
    __tablename__ = 'hint_numeric'
    id = Column(Integer, ForeignKey('hint.id'), primary_key=True)
    text = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'hintText'}

    @classmethod
    def create_unit_hint(cls, from_unit, to_unit):
        return TextHint(text='{} is {}'.format(format_value(from_unit, 1), convert(from_unit, 1, to_unit)))