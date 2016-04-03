import math
import random
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, Table, func, distinct
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, reconstructor, Session

from app.engine import convert
from app.extensions import db
from .Hint import TextHint, ScaleHint


class QuestionTaskAssociation(db.Model):
    __tablename__ = 'question_task_association'
    question_id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), primary_key=True)
    unit_system_constraint = Column(ENUM('metric', 'imperial', name='unit_system_constraint'), nullable=True)

    question = relationship('Question', back_populates='task_associations')
    task = relationship('Task')


class Question(db.Model):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    target_time = Column(Float, default=0)
    difficulty = Column(Float, default=0)
    # answered_times = Column(Integer, default=0) -- do we need this for recommendation?
    implicit_hint = Column(ENUM('None', 'Text', 'Scale', name='implicit_hint'))
    type = Column(String(50))
    enabled = Column(Boolean, default=True)

    task_associations = relationship('QuestionTaskAssociation')
    tasks = relationship('Task', secondary='question_task_association', back_populates="questions")
    taskrun_questions = relationship('TaskRunQuestion', back_populates='question')

    def answered_times(self):
        from app.models import TaskRunQuestion
        return Question.query.join(TaskRunQuestion).filter(TaskRunQuestion.correct != None,
                                                           TaskRunQuestion.question_id == self.id).count()

    def answered_first_time_times(self):
        from app.models import TaskRunQuestion, TaskRun
        return Question.query.join(TaskRunQuestion).join(TaskRun)\
            .filter(TaskRunQuestion.correct != None,
                    TaskRunQuestion.question_id == self.id)\
            .distinct(TaskRun.user_id).count()

    def expected_time(self, none_on_default=True) -> Optional[float]:
        if self.target_time > 0 or not none_on_default:
            return math.exp(self.target_time)
        else:
            return None

    def user_answered_times(self, user):
        from app.models import TaskRunQuestion, TaskRun
        anwered_times = Question.query.join(TaskRunQuestion).join(TaskRun)\
            .filter(TaskRunQuestion.correct != None,
                    TaskRunQuestion.question_id == self.id,
                    TaskRun.user_id == user.id) \
            .count()

    __mapper_args__ = {
        'polymorphic_identity': 'question',
        'polymorphic_on': type
    }


# close ended

class CloseEndedQuestion(Question):
    __tablename__ = 'question_closeEnded'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    question_type = Column(String)
    question_cz = Column(String)
    question_en = Column(String)
    image_name = Column(String, nullable=True)

    answers = relationship('CloseEndedAnswer')  # max 3 answers !!

    __mapper_args__ = {'polymorphic_identity': 'questionCloseEnded'}


class CloseEndedAnswer(db.Model):
    __tablename__ = 'answer_closeEnded'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("question_closeEnded.id"))
    value = Column(Float)  # eg. 10
    unit = Column(String)  # eg. cm
    correct = Column(Boolean)

    question = relationship('CloseEndedQuestion')

    @property
    def explanation(self):
        correct_question = [x for x in self.question.answers if x.correct and x.unit != self.unit]
        if len(correct_question) == 1:
            converted_value = convert.convert(self.unit, self.value, correct_question[0].unit)
            return convert.format_quantity(converted_value)
        else:
            return None


# numeric

class NumericQuestion(Question):
    __tablename__ = 'question_numeric'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    from_value = Column(Float)  # eg. 10
    from_unit = Column(String)  # eg. cm
    to_unit = Column(String)   # eg. m
    image_name = Column(String, nullable=True)

    @property
    def to_value(self):
        return convert.convert(self.from_unit, self.from_value, self.to_unit).magnitude

    @property
    def hint(self):
        isCurrency = "[currency]" in list(convert.ureg.parse_units(self.to_unit).dimensionality)
        if bool(random.getrandbits(1)) or isCurrency:
            return TextHint.create_unit_hint(self.from_unit, self.to_unit)
        else:
            return ScaleHint.create_unit_hint(self.from_unit, self.to_unit)

    __mapper_args__ = {'polymorphic_identity': 'questionNumeric'}


# scale

class ScaleQuestion(Question):
    __tablename__ = "question_scale"
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)
    scale_min = Column(Float)
    scale_max = Column(Float)
    from_value = Column(Float)  # eg. 10
    from_unit = Column(String)  # eg. cm
    to_unit = Column(String)   # eg. m

    @property
    def to_value(self):
        return convert.convert(self.from_unit, self.from_value, self.to_unit).magnitude

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
    value = Column(Float)  # eg. 10
    unit = Column(String)  # eg. cm
    presented_pos = Column(Integer)
    correct_pos = None

    question = relationship('SortQuestion')

    def normalized_value(self):
        return convert.to_normalized(self.unit, self.value)

    @property
    def explanation(self):
        min_unit = None
        for question in self.question.answers:
            normalized = convert.to_normalized(question.unit, 1)
            if min_unit is None or convert.to_normalized(min_unit, 1) > normalized:
                min_unit = question.unit

        if min_unit and min_unit != self.unit:
            converted_value = convert.convert(self.unit, self.value, min_unit)
            return convert.format_quantity(converted_value)
        else:
            return None


# currency

class CurrencyQuestion(Question):
    __tablename__ = 'question_currency'
    id = Column(Integer, ForeignKey('question.id'), primary_key=True)

    from_value = Column(Float)  # eg. 10
    from_unit = Column(String)  # eg. CZK
    to_unit = Column(String)   # eg. EUR
    # available_notes = Column(ARRAY(Integer, dimensions=2)) # (100, 4), (20, 1) -- 100,- 4x, 20,- 1x

    @hybrid_property
    def to_value(self):
        return convert.convert(self.from_unit, self.from_value, self.to_unit).magnitude

    @property
    def hint(self):
        return TextHint.create_unit_hint(self.from_unit, self.to_unit)

    __mapper_args__ = {'polymorphic_identity': 'questionCurrency'}