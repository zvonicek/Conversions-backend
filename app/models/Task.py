from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    name = Column(String)

    task_runs = relationship("TaskRun")


class TaskRun(db.Model):
    __tablename__ = 'task_run'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    date = Column(DateTime)

    task = relationship("Task")


