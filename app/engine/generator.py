import random

from app.extensions import db
from app.models import TaskRun, Question, Task, User
from app.models.Task import TaskRunQuestion


def generate_game(task, user):
    """
    Generates a new game
    :param task: task for which to generate a game
    :type task: Task
    :param user: user for which to generate a game
    :type user: User
    :return: freshly generated game
    :rtype: TaskRun
    """

    taskrun = TaskRun(task=task, user=user, questions=choose_questions(task, user, 5))
    db.session.add(taskrun)
    db.session.commit()
    return taskrun


def choose_questions(task: Task, user: User, number: int) -> [TaskRunQuestion]:
    """
    :param task: task for which to choose questions
    :param user: user for which to choose questions
    :param number: number of questions to choose
    :return: list of questions
    """

    # shuffle questions
    questions = random.sample(task.questions, len(task.questions))

    choosen_questions = []
    choosen_types_counts = {}

    for i in range(0, number):
        questions.sort(key=lambda k: question_priority(k, user, choosen_types_counts))

        choosen_questions.append(TaskRunQuestion(question=questions[0], position=i))
        choosen_types_counts[questions[0].type] = choosen_types_counts.get(questions[0].type, 0) + 1
        questions = questions[1:]

    return choosen_questions


def question_priority(question: Question, user: User, choosen_types_counts: {}) -> float:
    return 1.0
