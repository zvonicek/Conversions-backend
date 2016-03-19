import sys
import csv

from app.app import create_app
from app.config import config
from app.models import *
from app.extensions import db

app = create_app(config)
db.init_app(app)
db.app = app


def get_tasks():
    tasks = db.session.query(Task).all()
    tasks_dict = {}
    for task in tasks:
        tasks_dict[task.identifier] = task

    return tasks_dict


def get_skill(unit1, unit2):
    unit1, unit2 = min(unit1, unit2), max(unit1, unit2)

    skill = db.session.query(Skill).filter_by(unit1=unit1, unit2=unit2).first()
    if skill is None:
        skill = Skill(unit1=unit1, unit2=unit2, )
    return skill


def load_numeric(file):
    tasks = get_tasks()
    questions = []

    for row in file:
        task_name = row[0]

        if len(task_name) > 0 and task_name in tasks:
            global question
            if len(row[5]) > 0:
                question = NumericQuestion(difficulty=float(row[1].replace(',','.')), from_value=float(row[2].replace(',','.')), from_unit=row[3], to_unit=row[4], image_name=row[5], tasks=[tasks[task_name]])
            else:
                question = NumericQuestion(difficulty=float(row[1].replace(',','.')), from_value=float(row[2].replace(',','.')), from_unit=row[3], to_unit=row[4], tasks=[tasks[task_name]])

            question.skill = get_skill(question.from_unit, question.to_unit)
            questions.append(question)

    db.session.add_all(questions)
    db.session.commit()


def load_sort(file):
    tasks = get_tasks()
    questions = []

    for row in file:
        task_name = row[0]

        if len(task_name) > 0 and len(row[1]) > 0 and task_name in tasks:
            dimensionality = task_name.split('_')[0]
            question = SortQuestion(difficulty=float(row[2].replace(',','.')), dimensionality=dimensionality, order=row[1], tasks=[tasks[task_name]])
            questions.append(question)

            for i in range(0,4):
                value = row[3+i*2]
                unit = row[4+i*2]

                if len(value) > 0 and len(unit) > 0:
                    questions.append(SortAnswer(question=question, value=value, unit=unit, presented_pos=i))

    db.session.add_all(questions)
    db.session.commit()


def load_scale(file):
    tasks = get_tasks()
    questions = []

    for row in file:
        task_name = row[0]

        if len(task_name) > 0 and task_name in tasks:
            question = ScaleQuestion(difficulty=float(row[1].replace(',','.')), from_value=float(row[2].replace(',','.')), from_unit=row[3], to_unit=row[4], scale_min=float(row[5].replace(',','.')), scale_max=float(row[6].replace(',','.')), tasks=[tasks[task_name]])
            question.skill = get_skill(question.from_unit, question.to_unit)
            questions.append(question)

    db.session.add_all(questions)
    db.session.commit()


def load_closeended(file):
    tasks = get_tasks()
    questions = []

    for row in file:
        task_name = row[0]

        if len(task_name) > 0 and len(row[4]) > 0 and task_name in tasks:
            global question
            if len(row[3]) > 0:
                question = CloseEndedQuestion(difficulty=float(row[4].replace(',','.')), question_en=row[2], question_type=row[1], tasks=[tasks[task_name]], image_name=row[3])
            else:
                question = CloseEndedQuestion(difficulty=float(row[4].replace(',','.')), question_en=row[2], question_type=row[1], tasks=[tasks[task_name]])
            questions.append(question)

            for i in range(0,3):
                value = row[5+i*3]
                unit = row[6+i*3]
                correct = row[7+i*3]

                if len(value) > 0 and len(unit) > 0 and len(correct) > 0:
                    questions.append(CloseEndedAnswer(question=question, value=value, unit=unit, correct=correct))

    db.session.add_all(questions)
    db.session.commit()


def load_currency(file):
    tasks = get_tasks()
    questions = []

    for row in file:
        task_name = row[0]

        if len(task_name) > 0 and task_name in tasks:
            questions.append(CurrencyQuestion(difficulty=float(row[1].replace(',','.')), from_value=float(row[2].replace(',','.')), from_unit=row[3], to_unit=row[4], tasks=[tasks[task_name]]))

    db.session.add_all(questions)
    db.session.commit()


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        task_type = sys.argv[2]
        csv_file = csv.reader(file, delimiter=';')

        # skip the header
        next(csv_file, None)

        if task_type == "numeric":
            load_numeric(csv_file)
        elif task_type == "sort":
            load_sort(csv_file)
        elif task_type == "scale":
            load_scale(csv_file)
        elif task_type == "closeended":
            load_closeended(csv_file)
        elif task_type == "currency":
            load_scale(csv_file)