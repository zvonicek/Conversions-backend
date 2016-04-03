from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.engine.convert import format_unit, convert, format_value, format_quantity
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
    top_unit = Column(String)
    top_min = Column(Float)
    top_max = Column(Float)
    bottom_unit = Column(String)
    bottom_min = Column(Float)
    bottom_max = Column(Float)

    __mapper_args__ = {'polymorphic_identity': 'hintScale'}

    @classmethod
    def create_unit_hint(cls, from_unit, to_unit):
        converted_value = convert(from_unit, 1, to_unit).magnitude
        if converted_value < 1:
            converted_value = convert(to_unit, 1, from_unit).magnitude
            return ScaleHint(top_unit=from_unit, top_min=0, top_max=converted_value, bottom_unit=to_unit, bottom_min=0, bottom_max=1)
        else:
            return ScaleHint(top_unit=from_unit, top_min=0, top_max=1, bottom_unit=to_unit, bottom_min=0, bottom_max=converted_value)


class TextHint(Hint):
    __tablename__ = 'hint_numeric'
    id = Column(Integer, ForeignKey('hint.id'), primary_key=True)
    text = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'hintText'}

    @classmethod
    def create_unit_hint(cls, from_unit, to_unit):
        converted_value = convert(from_unit, 1, to_unit)
        if converted_value.magnitude > 0.001:
            value = format_quantity(converted_value)
            return TextHint(text='{} is {}'.format(format_value(from_unit, 1), value))
        else:
            converted_value = convert(to_unit, 1, from_unit)
            value = format_quantity(converted_value)
            return TextHint(text='{} is {}'.format(format_value(to_unit, 1), value))