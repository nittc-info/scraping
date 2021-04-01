from dataclasses import dataclass
from datetime import datetime, timedelta
from icalendar import Event as IEvent, vDate


@dataclass
class Date:
    year: int
    month: int
    day: int


@dataclass
class Event:
    subject: str = ''
    year: int = 0
    month_from: int = 0
    month_to: int = 0
    day_from: int = 0
    day_to: int = 0

    def to_ical_event(self) -> IEvent:
        dtstart = datetime(self.year, self.month_from, self.day_from)
        dtend = datetime(self.year, self.month_to, self.day_to)

        dtend += timedelta(days=+1)

        e = IEvent()
        e.add("summary", self.subject)
        e.add("dtstart", vDate(dtstart))
        e.add("dtend", vDate(dtend))

        return e
