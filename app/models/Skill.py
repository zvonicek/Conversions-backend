from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float, Table
from sqlalchemy.orm import relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    app_version = Column(String)
    language = Column(String)
    is_metric = Column(Boolean, nullable=True)
    skill_value = Column(Float, default=0)

    skills = relationship('UserSkill', back_populates="user")
    taskruns = relationship('TaskRun', back_populates="user")


class UserSkill(db.Model):
    __tablename__ = 'user_skill'

    # workaround to set default value even before inserting to db
    def __init__(self, **kwargs):
        if 'value' not in kwargs:
            kwargs['value'] = self.__table__.c.value.default.arg
        super(UserSkill, self).__init__(**kwargs)

    task_id = Column(Integer, ForeignKey('task.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    value = Column(Float, default=0)

    task = relationship('Task')
    user = relationship('User')