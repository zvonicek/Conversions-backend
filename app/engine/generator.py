from app.extensions import db
from app.models import TaskRun, Question
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


def choose_questions(task, user, number):
    """
    :param task: task for which to choose questions
    :type task: Task
    :param user: user for which to choose questions
    :type user: User
    :param number: number of questions to choose
    :type number: Integer
    :return: list of questions
    :rtype: [TaskRunQuestion]
    """

    run_questions = []
    questions = task.questions
    i = 0
    for question in questions:
        run_questions.append(TaskRunQuestion(question=question, position=i))
        i += 1

    return run_questions
