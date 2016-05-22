import random
import datetime
from math import sqrt
from typing import List

import math
from sqlalchemy import text

from app.engine.elo import compute_expected_response, compute_expected_response_time
from app.extensions import db
from app.models import TaskRun, Question, Task, User
from app.models.Task import TaskRunQuestion
from app.models.Skill import UserSkill


def generate_game(task: Task, user: User) -> TaskRun:
    """
    Generates a new game
    :param task: task for which to generate a game
    :param user: user for which to generate a game
    :return: freshly generated game
    """

    NUMBER_OF_QUESTIONS_FIRST = 5
    NUMBER_OF_QUESTIONS = 6

    taskrun = TaskRun(task_id=task.id, user_id=user.id)

    skill = taskrun.corresponding_skill(create_if_none=False)
    number_of_questions_load = NUMBER_OF_QUESTIONS_FIRST if skill is None else NUMBER_OF_QUESTIONS
    # use global skill if local skill does not exist
    skill_value = user.skill_value if skill is None else skill.value
    speed_value = skill.speed

    taskrun.questions = choose_questions(task, user, number_of_questions_load, skill_value, speed_value)
    db.session.add(taskrun)
    db.session.commit()
    return taskrun


def choose_questions(task: Task, user: User, number: int, skill: float, speed: float) -> [TaskRunQuestion]:
    """
    :param task: task for which to choose questions
    :param user: user for which to choose questions
    :param number: number of questions to choose
    :param skill: skill of the user for the current task
    :param speed: speed of the user for the current task
    :return: list of questions
    """

    if not user.is_metric:
        q = task.questions_m
    else:
        q = task.questions_i

    # shuffle questions
    questions = random.sample(q, len(q))

    answered_counts, last_answer_dates = fetch_questions_stats(questions, user)

    choosen_questions = []
    choosen_types_counts = {}

    for i in range(0, number):
        random.shuffle(questions)
        questions.sort(key=lambda k: question_priority(k, user, choosen_types_counts, answered_counts,
                                                       last_answer_dates, skill, speed), reverse=True)

        if len(questions) > 0:
            choosen_questions.append(TaskRunQuestion(question=questions[0], position=i))
            choosen_types_counts[questions[0].type] = choosen_types_counts.get(questions[0].type, 0) + 1
            questions = questions[1:]

    return choosen_questions


def question_priority(question: Question, user: User, choosen_types_counts: {}, answered_counts: {},
                      last_answer_dates: {}, skill_value: float, user_speed: float) -> float:
    # a hack to keep order of questions consistent when using testing task
    if question.tasks[0].identifier == "test":
        return question.id

    RESPONSE_GOAL = 0.75

    ANSWERED_COUNT_WEIGHT = 10
    SAME_TYPE_PENALTY_WEIGHT = 10
    TIME_WEIGHT = 120
    PROBABILITY_WEIGHT = 10

    # score for total answered count for the user
    answered_count_score = 1. / sqrt(1 + answered_counts.get(question.id, 0))
    # score for number of selected questions of the same type
    same_type_penalty_score = 1. / sqrt(1 + choosen_types_counts.get(question.type, 0))

    # score for time from last answer of the question
    if question.id in last_answer_dates:
        time_score = -1. / (last_answer_dates[question.id]) if last_answer_dates[question.id] > 0 else -1
    else:
        time_score = 0

    # score for probability of correct answer
    expected_time = compute_expected_response_time(user_speed, question.target_time)
    expected_response = compute_expected_response(skill_value, question.difficulty, expected_time)
    if RESPONSE_GOAL > expected_response:
        probability_score = expected_response / RESPONSE_GOAL
    else:
        probability_score = (1 - expected_response) / (1 - RESPONSE_GOAL)

    return answered_count_score * ANSWERED_COUNT_WEIGHT + same_type_penalty_score * SAME_TYPE_PENALTY_WEIGHT + time_score * TIME_WEIGHT + probability_score * PROBABILITY_WEIGHT


def fetch_questions_stats(questions: List[Question], user: User):
    answered_counts_rows = db.session.execute(text('SELECT question.id, count(question.id) AS count FROM question '
                                                   'JOIN taskrun_question ON taskrun_question.question_id = question.id '
                                                   'JOIN taskrun ON taskrun_question.taskrun_id = taskrun.id '
                                                   'WHERE taskrun_question.correct is not null AND taskrun.user_id = :userid '
                                                   'AND question.id IN :questions '
                                                   'GROUP BY question.id'),
                                              params={"userid": user.id,
                                                      "questions": tuple(map((lambda x: x.id), questions))})

    answered_counts = dict((x.id, x.count) for x in answered_counts_rows)

    last_answer_date_rows = db.session.execute(text('SELECT question.id, MAX(taskrun.date) AS date FROM question '
                                                    'JOIN taskrun_question ON taskrun_question.question_id = question.id '
                                                    'JOIN taskrun ON taskrun_question.taskrun_id = taskrun.id '
                                                    'WHERE taskrun_question.correct is not null AND taskrun.user_id = :userid '
                                                    'AND question.id IN :questions '
                                                    'GROUP BY question.id'),
                                               params={"userid": user.id,
                                                       "questions": tuple(map((lambda x: x.id), questions))})

    now = datetime.datetime.now()
    last_answer_dates = dict((x.id, (now - x.date).total_seconds()) for x in last_answer_date_rows)

    return answered_counts, last_answer_dates
