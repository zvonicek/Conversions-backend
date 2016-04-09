import math

from app.models.Task import TaskRunQuestion


def compute_expected_response(user_skill: float, difficulty: float, response_time: float = 1) -> float:
    # the easier is the question for the user, the higher is the expected response
    return 1. / (1 + math.exp(difficulty - math.log(response_time) - user_skill))


def compute_user_skill_delta(response: float, expected_response: float) -> float:
    K_SUCCESS = 3.4
    K_FAILURE = 0.4

    if response >= expected_response:
        delta = K_SUCCESS * (response - expected_response)
    else:
        delta = K_FAILURE * (response - expected_response)

    return delta


def compute_difficulty_delta(response: float, expected_response: float, first_attempts_count: float) -> float:
    ALPHA = 1.0
    BETA = 0.06
    # each question has initial difficulty which is treated as a regular rank, so we do not lower first_attempts_count by one
    K = ALPHA / (1 + BETA * first_attempts_count)

    delta = K * (expected_response - response)  # = K * ((1 - response) - (1 - expected_response))
    return delta


def compute_target_time_delta(response_time: float, target_time: float, attempts_count: int) -> float:
    return (math.log(response_time) - target_time) / attempts_count


def update(question_run: TaskRunQuestion):
    """
    Updates model with the provided TaskRunQuestion
    :param question_run: question to update
    """

    # update target time
    if question_run.is_users_first_attempt:
        # update only on first attempt, otherwase it may be influenced by learning
        question_run.question.target_time += compute_target_time_delta(question_run.time,
                                                                       question_run.question.target_time,
                                                                       question_run.question.answered_times())

    # update skills
    response = question_run.get_score()
    user_skill = question_run.taskrun.corresponding_skill()

    # task skill
    expected_response = compute_expected_response(user_skill.value, question_run.question.difficulty, question_run.time)
    user_skill_delta = compute_user_skill_delta(response, expected_response)
    user_skill.value += user_skill_delta
    print("respose:", response, "expected response:", expected_response, "skill delta:", user_skill_delta)

    # global user skill
    expected_response_global = compute_expected_response(question_run.taskrun.user.skill_value, question_run.question.difficulty, question_run.time)
    user_skill_delta_global = compute_user_skill_delta(response, expected_response_global)
    question_run.taskrun.user.skill_value += user_skill_delta_global

    # update question difficuilty
    if question_run.is_users_first_attempt:
        # update only on first attempt, otherwase it may be influenced by learning
        question_run.question.difficulty += compute_difficulty_delta(response,
                                                                     expected_response,
                                                                     question_run.question.answered_first_time_times())
