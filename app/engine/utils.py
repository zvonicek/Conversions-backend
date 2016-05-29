from app.models import Task


def get_tolerance(unit: str, value: float) -> float:
    """
    Returns allowed tolerance for the specified unit and value
    :param unit: input unit
    :param value: input value
    :return: float representation of the allowed tolerance
    """

    FIXED_TOLERANCE_PERCENTS = 10

    if unit == "degF":
        return 15.0
    elif unit == "degC":
        return 8.0
    else:
        return value * FIXED_TOLERANCE_PERCENTS / 100