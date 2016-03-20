import datetime
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float, select, func, join
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, column_property, aliased

from app.extensions import db
from app.models.Skill import UserSkill
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
    user = relationship("User", back_populates="taskruns")
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

    def corresponding_skill(self) -> UserSkill:
        """
        Returns skill corresponding to the user and the question of the TaskRunQuestion
        """

        skill = UserSkill.query \
            .join(UserSkill.skill) \
            .filter(UserSkill.user_id == self.taskrun.user_id,
                    UserSkill.skill_id == self.question.skill_id
                    ) \
            .first()

        if skill is None:
            skill = UserSkill(skill_id=self.question.skill_id, user_id=self.taskrun.user_id)
            db.session.add(skill)

        return skill

    def get_score(self) -> Optional[float]:
        """
        Computes score of the answered question (how good the answer was)
        :return: score [0, 1] of the answer, null if question not answered yet
        """

        SPEED_PENALTY_SLOPE = 0.6

        if self.correct is None or self.time is None:
            return None

        if self.correct:
            # answer was correct

            if self.hint_shown:
                # hint was shown - user did not answer correctly on the first try and needed hint
                return 0.2
            else:
                # user answered correctly on first try without using hint
                global accuracy
                accuracy = 1

                if 'answer' in self.answer and 'tolerance' in self.answer and 'correctAnswer' in self.answer:
                    # question has allowed tolerance, can adjust accuracy analyzing that
                    accuracy = 1 - ((self.answer["correctAnswer"] - self.answer["answer"]) / self.answer["tolerance"])

                expected_time = self.question.expected_time(none_on_default=False)
                global speed
                if expected_time > self.time:
                    speed = 1
                else:
                    speed = SPEED_PENALTY_SLOPE ** ((self.time / expected_time) - 1)

                print("speed: " + str(speed) + " accuracy:" + str(accuracy))
                return 0.4 + 0.3 * accuracy + 0.3 * speed
        else:
            # answer was not correct
            return 0
