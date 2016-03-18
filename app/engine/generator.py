import random

from app.extensions import db
from app.models import TaskRun, Question, Task, User
from app.models.Task import TaskRunQuestion


def generate_game(task: Task, user: User) -> TaskRun:
    """
    Generates a new game
    :param task: task for which to generate a game
    :param user: user for which to generate a game
    :return: freshly generated game
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
    questions = Question.query.filter(Question.tasks.contains(task)).all()
    questions = random.sample(task.questions, len(questions))

    choosen_questions = []
    choosen_types_counts = {}

    for i in range(0, number):
        random.shuffle(questions)
        questions.sort(key=lambda k: question_priority(k, user, choosen_types_counts), reverse=True)

        choosen_questions.append(TaskRunQuestion(question=questions[0], position=i))
        choosen_types_counts[questions[0].type] = choosen_types_counts.get(questions[0].type, 0) + 1
        questions = questions[1:]

    return choosen_questions


def question_priority(question: Question, user: User, choosen_types_counts: {}) -> float:
    if question.type in choosen_types_counts:
        return 1 - choosen_types_counts[question.type]
    else:
        return 1.0
