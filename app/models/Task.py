from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float
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
    __tablename__ = 'taskrun'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    date = Column(DateTime)

    task = relationship("Task")
    user = relationship("User")
    questions = relationship("TaskRunQuestion", back_populates="taskrun")


class TaskRunQuestion(db.Model):
    __tablename__ = 'taskrun_question'
    taskrun_id = Column(Integer, ForeignKey("taskrun.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("question.id"), primary_key=True)
    position = Column(Integer)
    correct = Column(Boolean, nullable=True)
    time = Column(Integer, nullable=True)
    hintShown = Column(Boolean, nullable=True)
    answer = Column(Float, nullable=True)

    taskrun = relationship("TaskRun")
    question = relationship("Question")