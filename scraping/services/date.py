from datetime import datetime, timezone, timedelta
from scraping.models.events import Date

JST = timezone(timedelta(hours=+9), 'JST')


def today() -> (int, int, int):
    today = datetime.now(JST)
    year, month, day = today.year, today.month, today.day

    if 1 <= month <= 3:
        year -= 1

    return (year, month, day)


def today_date() -> Date:
    year, month, day = today()
    return Date(year, month, day)


def today_str() -> str:
    year, month, day = today()
    return f'{year}-{month:02}-{day:02}'
