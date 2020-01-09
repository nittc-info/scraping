import re
from libs.wordconv import z2h
from datetime import datetime, timezone, timedelta
from icalendar import Calendar
from model.eventdata import EventData
from libs.web import get_html_source, remove_tags


class EventExtractor:
    # ＜１月＞
    RE_MONTH = re.compile(r'＜([０-９]+)月＞')
    # １日（月）
    RE_EVENT_D = re.compile(r"([０-９]+)日（.）　(.*)")
    # １日（月）〜２日（火）
    RE_EVENT_D_D = re.compile(r"([０-９]+)日（.）～([０-９]+)日（.）　(.*)")
    # １日（月）〜１月２日（火）
    RE_EVENT_D_MD = re.compile(r"([０-９]+)日（.）～([０-９]+)月([０-９]+)日（.）　(.*)")

    def __init__(self):
        jst = timezone(timedelta(hours=+9), 'JST')
        self.today = datetime.now(jst)
        self.today_str = self.today.strftime('%Y%m%d')
        self.current_month = 4
        self.current_year = self.today.year
        # 1-3月のとき、来年の話になってしまうので
        if 1 <= self.today.month <= 3:
            self.current_year -= 1

    def create_calendar(self) -> Calendar:
        cal = Calendar()
        time = self.today.strftime('%Y.%m.%d')
        cal.add('prodid', f'津山高専行事予定{self.current_year}年度版（{time}時点）')
        cal.add('version', '2.0')
        return cal

    def parse(self, html_source: str):
        html_lines = (remove_tags(l) for l in html_source.split('\n'))
        parsed_events = (self.parse_line(l) for l in html_lines)
        return (event for event in parsed_events if event is not None)

    def parse_line(self, html_line: str):
        match = self.RE_EVENT_D_MD.findall(html_line)
        if match:
            return self.parse_event_d_md_line(match[0])

        match = self.RE_EVENT_D_D.findall(html_line)
        if match:
            return self.parse_event_d_d_line(match[0])

        match = self.RE_EVENT_D.findall(html_line)
        if match:
            return self.parse_event_d_line(match[0])

        match = self.RE_MONTH.findall(html_line)
        if match:
            self.parse_month_line(match)
        return None

    def parse_month_line(self, match: [re.Match]):
        self.current_month = z2h(match[0])
        if self.current_month == 1:
            self.current_year += 1

    def parse_event_d_line(self, match: [re.Match]):
        event = EventData()
        event.year = self.current_year
        event.month_from = event.month_to = self.current_month
        event.day_from = event.day_to = z2h(match[0])
        event.subject = match[1]
        return event

    def parse_event_d_d_line(self, match: [re.Match]):
        event = EventData()
        event.year = self.current_year
        event.month_from = event.month_to = self.current_month
        event.day_from = z2h(match[0])
        event.day_to = z2h(match[1])
        event.subject = match[2]
        return event

    def parse_event_d_md_line(self, match: [re.Match]):
        event = EventData()
        event.year = self.current_year
        event.month_from = self.current_month
        event.month_to = z2h(match[1])
        event.day_from = z2h(match[0])
        event.day_to = z2h(match[2])
        event.subject = match[3]
        return event

    def add_events_to_calender(self, cal: Calendar, events: [EventData]):
        for event in events:
            cal.add_component(event.to_ical_event())
        return cal

    def extract(self) -> str:
        url = f"http://www.tsuyama-ct.ac.jp/gyoujiVer4/gyouji.html"
        cal = self.create_calendar()
        source = get_html_source(url)
        events = self.parse(source)
        cal = self.add_events_to_calender(cal, events)
        return cal.to_ical().decode("utf-8")
