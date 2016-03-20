from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float, Table
from sqlalchemy.orm import relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    app_version = Column(String)
    language = Column(String)

    skills = relationship('UserSkill', back_populates="user")
    taskruns = relationship('TaskRun', back_populates="user")


class Skill(db.Model):
    __tablename = 'skill'
    id = Column(Integer, primary_key=True)
    unit1 = Column(String)
    unit2 = Column(String)

    users = relationship('UserSkill', back_populates="skill")
    questions = relationship('Question', back_populates="skill")


class UserSkill(db.Model):
    __tablename__ = 'user_skill'

    # workaround to set default value even before inserting to db
    def __init__(self, **kwargs):
        if 'value' not in kwargs:
            kwargs['value'] = self.__table__.c.value.default.arg
        super(UserSkill, self).__init__(**kwargs)

    skill_id = Column(Integer, ForeignKey('skill.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    value = Column(Float, default=0)

    skill = relationship('Skill')
    user = relationship('User')