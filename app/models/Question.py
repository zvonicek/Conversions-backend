import math
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, Table
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, reconstructor, Session

from app.engine.convert import convert, to_normalized
from app.extensions import db
from .Hint import TextHint

question_task_association = Table('question_task_association', db.Model.metadata,
                                  Column('question_id', Integer, ForeignKey('question.id')),
                                  Column('task_id', Integer, ForeignKey('task.id')),
                                  )


class Question(db.Model):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey('skill.id'))
    target_time = Column(Float, default=0)
    difficulty = Column(Float, default=0)
    # answered_times = Column(Integer, default=0) -- do we need this for recommendation?
    implicit_hint = Column(ENUM('None', 'Text', 'Scale', name='implicit_hint'))
    type = Column(String(50))

    tasks = relationship('Task', secondary=question_task_association, back_populates="questions")
    skill = relationship('Skill', back_populates='questions')
    taskrun_questions = relationship('TaskRunQuestion', back_populates='question')

    def answered_times(self):
        from app.models import TaskRunQuestion
        return Question.query.join(TaskRunQuestion).filter(TaskRunQuestion.correct != None,
                                                           TaskRunQuestion.question_id == self.id).count()

    def expected_time(self, none_on_default=True) -> Optional[float]:
        if self.target_time > 0 or not none_on_default:
            return math.exp(self.target_time)
        else:
            return None

    __mapper_args__ = {
        'polymorphic_identity': 'question',
        'polymorphic_on': type
    }


# close ended

class CloseEndedQuestion(Question):
    __tablename__ = 'question_closeEnded'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    question_type = Column(String)
    #question_cz = Column(String)
    question_en = Column(String)
    image_name = Column(String, nullable=True)

    answers = relationship('CloseEndedAnswer')  # max 3 answers !!

    __mapper_args__ = {'polymorphic_identity': 'questionCloseEnded'}


class CloseEndedAnswer(db.Model):
    __tablename__ = 'answer_closeEnded'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("question_closeEnded.id"))
    value = Column(Integer)  # eg. 10
    unit = Column(String)  # eg. cm
    correct = Column(Boolean)

    question = relationship('CloseEndedQuestion')


# numeric

class NumericQuestion(Question):
    __tablename__ = 'question_numeric'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    from_value = Column(Integer)  # eg. 10
    from_unit = Column(String)  # eg. cm
    to_unit = Column(String)   # eg. m
    image_name = Column(String, nullable=True)

    @property
    def to_value(self):
        return convert(self.from_unit, self.from_value, self.to_unit).magnitude

    @property
    def hint(self):
        return TextHint.create_unit_hint(self.from_unit, self.to_unit)

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

    @property
    def to_value(self):
        return convert(self.from_unit, self.from_value, self.to_unit).magnitude

    __mapper_args__ = {'polymorphic_identity': 'questionScale'}


# sort

class SortQuestion(Question):
    __tablename__ = 'question_sort'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    dimensionality = Column(ENUM('length', 'mass', 'area', 'volume', 'temperature', 'currency', name='e_dimensionality'))
    order = Column(ENUM('asc', 'desc', name='e_order'))
    min_label = ""
    max_label = ""

    answers = relationship('SortAnswer')  # max 4 answers !!

    __mapper_args__ = {'polymorphic_identity': 'questionSort'}

    @reconstructor
    def init_on_load(self):
        self.min_label = {
            "length": "smallest",
            "mass": "lightest",
            "area": "smallest",
            "volume": "smallest",
            "currency": "cheapest"
        }[self.dimensionality]

        self.max_label = {
            "length": "largest",
            "mass": "heaviest",
            "area": "largest",
            "volume": "largest",
            "currency": "most expensive"
        }[self.dimensionality]

        if self.order == 'desc':
            self.min_label, self.max_label = self.max_label, self.min_label

    def sorted_answers(self):
        is_reverse = self.order == 'desc'
        answers = sorted(self.answers, key=lambda x: x.normalized_value(), reverse=is_reverse)
        for i in range(0, len(answers)):
            answers[i].correct_pos = i

        return answers


class SortAnswer(db.Model):
    __tablename__ = 'answer_sort'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("question_sort.id"))
    value = Column(Integer)  # eg. 10
    unit = Column(String)  # eg. cm
    presented_pos = Column(Integer)
    correct_pos = None

    question = relationship('SortQuestion')

    def normalized_value(self):
        return to_normalized(self.unit, self.value)


# currency

class CurrencyQuestion(Question):
    __tablename__ = 'question_currency'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)

    from_value = Column(Integer)  # eg. 10
    from_unit = Column(String)  # eg. CZK
    to_unit = Column(String)   # eg. EUR
    # available_notes = Column(ARRAY(Integer, dimensions=2)) # (100, 4), (20, 1) -- 100,- 4x, 20,- 1x

    @hybrid_property
    def to_value(self):
        return convert(self.from_unit, self.from_value, self.to_unit).magnitude

    @property
    def hint(self):
        return TextHint.create_unit_hint(self.from_unit, self.to_unit)

    __mapper_args__ = {'polymorphic_identity': 'questionCurrency'}


# event listeners
#
# @db.event.listens_for(NumericQuestion, "after_insert")
# def numeric_after_insert(mapper, connection, target):
#     unit1, unit2 = min(target.from_unit, target.to_unit), max(target.from_unit, target.to_unit)
#
#     skill = db.session.query(Skill).filter_by(unit1=unit1, unit2=unit2).first()
#     if skill is None:
#         skill = Skill(unit1=unit1, unit2=unit2, )
#
#     target.skill = skill
