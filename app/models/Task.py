import datetime
from typing import Optional

import math
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float, select, func, join, sql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property, aliased

from app.extensions import db
from app.models.Question import QuestionTaskAssociation, Question
from app.models.Skill import UserSkill


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    name = Column(String)

    task_runs = relationship("TaskRun", back_populates="task")
    questions = relationship('Question', secondary='question_task_association', back_populates="tasks")

    # questions_m and questions_i are relationshipts to questions that filters only universal questions
    # (unit_system_constraint == None) and questions that involves solely metric (_m) or imperial (_i) conversions.
    # This is particularly the case in CloseEnded questions in combination with "combined" task where we want to decide
    # upon the user's native unit system if present metric or imperial questions (so if having metric, show imperial
    # questions like 'estimate eight of a tea cup' with answers in imperial and vice versa)
    questions_m = relationship('Question', secondary='question_task_association',
                               secondaryjoin=sql.and_(QuestionTaskAssociation.question_id == Question.id,
                                                      Question.enabled != False,
                                                      sql.or_(QuestionTaskAssociation.unit_system_constraint == "metric",
                                                              QuestionTaskAssociation.unit_system_constraint == None)
                                                      ))
    questions_i = relationship('Question', secondary='question_task_association',
                               secondaryjoin=sql.and_(QuestionTaskAssociation.question_id == Question.id,
                                                      Question.enabled != False,
                                                      sql.or_(
                                                          QuestionTaskAssociation.unit_system_constraint == "imperial",
                                                          QuestionTaskAssociation.unit_system_constraint == None)
                                                      ))


class TaskRun(db.Model):
    __tablename__ = 'taskrun'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    completed = Column(Boolean, nullable=True)
    summary = Column(JSONB, nullable=True)

    task = relationship("Task")
    user = relationship("User", back_populates="taskruns")
    questions = relationship("TaskRunQuestion", back_populates="taskrun", order_by="TaskRunQuestion.position")

    def corresponding_skill(self, create_if_none=True) -> UserSkill:
        """
        Returns skill corresponding to the user and the question of the TaskRunQuestion
        """

        skill = UserSkill.query \
            .filter(UserSkill.user_id == self.user_id,
                    UserSkill.task_id == self.task_id
                    ) \
            .first()

        if skill is None and create_if_none:
            skill = UserSkill(task_id=self.task_id, user_id=self.user_id)
            db.session.add(skill)

        return skill

    def allow_speed_feedback(self) -> Boolean:
        skill = self.corresponding_skill(create_if_none=False)
        return skill is not None and skill.value > 0.5


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

    @hybrid_property
    def is_users_first_attempt(self) -> bool:
        """
        Checks whether the corresponding user answered to the corresponding question for the first time
        """

        count = TaskRunQuestion.query \
            .join(TaskRunQuestion.taskrun) \
            .filter(TaskRunQuestion.taskrun_id != self.taskrun_id,
                    TaskRunQuestion.question_id == self.question_id,
                    TaskRun.user_id == self.taskrun.user_id,
                    TaskRunQuestion.correct != None) \
            .count()

        return count == 0

    def get_score(self) -> Optional[float]:
        """
        Computes score of the answered question (how good the answer was)
        :return: score [0, 1] of the answer, null if question not answered yet
        """

        if self.correct is None:
            return None

        if self.correct:
            # answer was correct

            if self.hint_shown:
                # hint was shown - user did not answer correctly on the first try and needed hint
                return 0.2
            else:
                # user answered correctly on first try without using hint
                accuracy = 1

                if 'answer' in self.answer and 'tolerance' in self.answer and 'correctAnswer' in self.answer:
                    answer, tolerance, correctAnswer = float(self.answer["answer"]), float(
                        self.answer["tolerance"]), float(self.answer["correctAnswer"])
                    correctAnswer = round(correctAnswer)
                    
                    # question has allowed tolerance, can adjust accuracy analyzing that
                    accuracy = 1 - (abs(correctAnswer - answer) / tolerance)

                return 0.6 + 0.4 * accuracy
        else:
            # answer was not correct
            return 0
