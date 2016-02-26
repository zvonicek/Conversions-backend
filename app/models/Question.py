from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.engine.convert import convert
from app.extensions import db

question_task_association = Table('question_task_association', db.Model.metadata,
                                  Column('question_id', Integer, ForeignKey('question.id')),
                                  Column('task_id', Integer, ForeignKey('task.id')),
                                  )


class Question(db.Model):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    time_fast = Column(Integer, nullable=True)
    time_neutral = Column(Integer, nullable=True)
    difficulty = Column(ENUM('Easy', 'Medium', 'Hard', name='difficulty'))
    type = Column(String(50))

    tasks = relationship('Task', secondary=question_task_association, back_populates="questions")

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

    answers = relationship('CloseEndedAnswer')

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

    question = relationship('CloseEndedQuestion')


# numeric

class NumericQuestion(Question):
    __tablename__ = 'question_numeric'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    from_value = Column(Integer)  # eg. 10
    from_unit = Column(String)  # eg. cm
    to_unit = Column(String)   # eg. m
    image_path = Column(String, nullable=True)
    # doplnit hint

    @hybrid_property
    def to_value(self):
        return convert(self.from_unit, self.from_value, self.to_unit).magnitude

    __mapper_args__ = {'polymorphic_identity': 'questionNumeric'}


# scale

class ScaleQuestion(Question):
    __tablename__ = "question_scale"
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    scale_min = Column(Float)
    scale_max = Column(Float)
    from_value = Column(Integer)  # eg. 10
    from_unit = Column(String)  # eg. cm
    to_unit = Column(String)   # eg. m

    @hybrid_property
    def to_value(self):
        return convert(self.from_unit, self.from_value, self.to_unit).magnitude

    __mapper_args__ = {'polymorphic_identity': 'questionScale'}


# sort

class SortQuestion(Question):
    __tablename__ = 'question_sort'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    quantity = Column(String)  # length, weight, ...
    order = Column(ENUM('Asc', 'Desc', name='order'))

    answers = relationship('SortAnswer')

    __mapper_args__ = {'polymorphic_identity': 'questionSort'}


class SortAnswer(db.Model):
    __tablename__ = 'answer_sort'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("question_sort.id"))
    value = Column(Integer)  # eg. 10
    unit = Column(String) # eg. cm
    #correct_pos = Column(Integer)
    presnted_pos = Column(Integer)

    question = relationship('SortQuestion')
