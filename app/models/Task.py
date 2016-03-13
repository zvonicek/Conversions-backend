import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.Question import question_task_association


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    name = Column(String)

    task_runs = relationship("TaskRun", back_populates="task")
    questions = relationship('Question', secondary=question_task_association, back_populates="tasks")


class TaskRun(db.Model):
    __tablename__ = 'taskrun'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    completed = Column(Boolean, nullable=True)

    task = relationship("Task")
    user = relationship("User")
    questions = relationship("TaskRunQuestion", back_populates="taskrun", order_by="TaskRunQuestion.position")


class TaskRunQuestion(db.Model):
    __tablename__ = 'taskrun_question'
    taskrun_id = Column(Integer, ForeignKey("taskrun.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("question.id"), primary_key=True)
    position = Column(Integer)
    correct = Column(Boolean, nullable=True)
    time = Column(Float, nullable=True)
    hint_shown = Column(Boolean, nullable=True)
    answer = Column(JSONB, nullable=True)

    taskrun = relationship("TaskRun")
    question = relationship("Question")