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


class Skill(db.Model):
    __tablename = 'skill'
    id = Column(Integer, primary_key=True)

    users = relationship('UserSkill', back_populates="skill")
    questions = relationship('Question', back_populates="skill")


class UserSkill(db.Model):
    __tablename__ = 'user_skill'
    skill_id = Column(Integer, ForeignKey('skill.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    value = Column(Float, default=0)

    skill = relationship('Skill')
    user = relationship('User')