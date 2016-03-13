from app.models import Task


def get_tolerance(unit: str, value: float) -> float:
    FIXED_TOLERANCE_PERCENTS = 10

    return value * FIXED_TOLERANCE_PERCENTS / 100