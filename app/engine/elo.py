import math

from app.models.Task import TaskRunQuestion
def compute_target_time_delta(response_time: float, target_time: float, attempts_count: int) -> float:
    return (math.log(response_time) - target_time) / attempts_count


def update(question_run: TaskRunQuestion):
    q_difficulty = question_run.question.difficulty

    if question_run.is_users_first_attempt:
        # update only on first attempt, otherwase may be influenced by learning
        question_run.question.target_time += compute_target_time_delta(question_run.time,
                                                                      question_run.question.target_time,
                                                                      question_run.question.answered_times())


