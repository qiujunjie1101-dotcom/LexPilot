"""账期天数换算与工作日核验工具。"""
from __future__ import annotations

from datetime import date, timedelta


def as_days(value: object) -> int:
    """将归一化字段中的账期值转成天数，缺失按 0 处理（与旧规则引擎一致）。"""
    return int(value or 0)


def exceeds(days: int, limit: int) -> bool:
    return days > limit


def working_days_between(start: date, end: date) -> int:
    if end < start:
        return -working_days_between(end, start)
    days = 0
    cursor = start
    while cursor < end:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            days += 1
    return days
