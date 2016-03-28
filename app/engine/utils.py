from app.models import Task


def get_tolerance(unit: str, value: float) -> float:
    FIXED_TOLERANCE_PERCENTS = 10

    if unit == "degF":
        return 15.0
    elif unit == "degC":
        return 8.0
    else:
        return value * FIXED_TOLERANCE_PERCENTS / 100