from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.extensions import db


class Question(db.Model):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    time_fast = Column(Integer)
    time_neutral = Column(Integer)
    difficulty = Column(ENUM('Easy', 'Medium', 'Hard', name='difficulty'))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'question',
        'polymorphic_on': type
    }


# close ended

class CloseEndedQuestion(Question):
    __tablename__ = 'question_closeEnded'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    question_cz = Column(String)
    question_en = Column(String)

    answers = relationship('question_closeEnded_answer')

    __mapper_args__ = {'polymorphic_identity': 'questionCloseEnded'}


class CloseEndedAnswer(db.Model):
    __tablename__ = 'answer_closeEnded'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("question_closeEnded.id"))
    answer_en = Column(String)
    answer_cz = Column(String)
    explanation_en = Column(String)
    explanation_cz = Column(String)
    correct = Column(Boolean)

    question = relationship('question_closeEnded')


# numeric

class NumericQuestion(Question):
    __tablename__ = 'question_numeric'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    fromVal = Column(Float)
    toVal = Column(Float)
    fromUnut = Column(String)
    toUnit = Column(String)
    correctTolerance = Column(Float)
    imagePath = Column(String)
    # doplnit hint

    __mapper_args__ = {'polymorphic_identity': 'questionNumeric'}


# scale

class ScaleQuestion(Question):
    __tablename__ = "question_scale"
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    task_en = Column(String)
    task_cz = Column(String)
    scale_min = Column(Float)
    scale_max = Column(Float)
    correctVal = Column(Float)
    correctTolerance = Column(Float)
    fromUnit = Column(String) # to by mel byt FK
    toUnit = Column(String)

    __mapper_args__ = {'polymorphic_identity': 'questionScale'}


# sort

class SortQuestion(Question):
    __tablename__ = 'question_sort'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    question_en = Column(String)
    question_cz = Column(String)
    top_desc_en = Column(String)
    top_desc_cz = Column(String)
    bottom_desc_en = Column(String)
    bottom_desc_cz = Column(String)

    answers = relationship('question_closeEnded_answer')

    __mapper_args__ = {'polymorphic_identity': 'questionSort'}


class SortAnswer(db.Model):
    __tablename__ = 'answer_sort'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("question_sort.id"))
    answer_en = Column(String)
    answer_cz = Column(String)
    correct_pos = Column(Integer)
    presnted_pos = Column(Integer)
    explanation_en = Column(String)
    explanation_cz = Column(String)

    question = relationship('question_closeEnded')
