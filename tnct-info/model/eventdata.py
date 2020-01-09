from datetime import datetime
from icalendar import Event, vDate


class EventData:
    def __init__(self):
        self.subject = ""
        self.year = ""
        self.month_from = ""
        self.month_to = ""
        self.day_from = ""
        self.day_to = ""

    def to_ical_event(self):
        ievent = Event()
        ievent.add("summary", self.subject)
        dt = datetime(self.year, self.month_from, self.day_from)
        ievent.add("dtstart", vDate(dt))
        dt = datetime(self.year, self.month_to, self.day_to)
        ievent.add("dtend", vDate(dt))
        return ievent
