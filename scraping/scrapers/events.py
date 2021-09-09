import re
from unicodedata import normalize
from icalendar import Calendar
from scraping.models.events import Event, Date
from scraping.services import web, dateutil, logger

EVENTS_URL = 'http://www.tsuyama-ct.ac.jp/gyoujiVer4/gyouji.html'

# ＜１月＞
RE_MONTH = re.compile(r'＜([０-９]+)月＞')
# １日（月）
RE_EVENT_D = re.compile(r"([０-９]+)日（.）　?(.*)")
# １日（月）〜２日（火）
RE_EVENT_D_D = re.compile(r"([０-９]+)日（.）～([０-９]+)日（.）　?(.*)")
# １日（月）〜１月２日（火）
RE_EVENT_D_MD = re.compile(r"([０-９]+)日（.）～([０-９]+)月([０-９]+)日（.）　?(.*)")


def add_tag(subject: str):
    keyword = "寮"
    if keyword in subject:
        return f"【寮】{subject}"
    return f"【学校】{subject}"


def remove_tags(value: str):
    value = value.replace("  ", "")
    return re.sub('<[^>]*>', '', value)


def z2h(s: str) -> int:
    return int(normalize('NFKC', s))


def generate_ical(events: list[Event], today: Date) -> str:
    cal = Calendar()
    today_str = dateutil.today_str(".")
    cal.add('prodid', f'津山高専行事予定{today.year}年度版（{today_str}時点）')
    cal.add('version', '2.0')

    for event in events:
        try:
            cal.add_component(event.to_ical_event())
        except ValueError as e:
            # 月をまたがる予定のパースで落ちるのを防ぐ
            logger.warning(f'{e}: {event.subject}')

    return cal.to_ical().decode("utf-8")


def parse_month_line(s: str, date: Date) -> Date:
    date.month = z2h(s)
    if date.month == 1:
        date.year += 1
    return date


def parse_event_d_line(match: re.Match, date: Date) -> Event:
    event = Event()
    event.year = date.year
    event.month_from = event.month_to = date.month
    event.day_from = event.day_to = z2h(match[0])
    event.subject = add_tag(match[1])
    return event


def parse_event_d_d_line(match: re.Match, date: Date) -> Event:
    event = Event()
    event.year = date.year
    event.month_from = event.month_to = date.month
    event.day_from = z2h(match[0])
    event.day_to = z2h(match[1])
    event.subject = add_tag(match[2])
    return event


def parse_event_d_md_line(match: re.Match, date: Date) -> Event:
    event = Event()
    event.year = date.year
    event.month_from = date.month
    event.month_to = z2h(match[1])
    event.day_from = z2h(match[0])
    event.day_to = z2h(match[2])
    event.subject = add_tag(match[3])
    return event


def parse_line(line: str, date: Date) -> tuple[Event, Date]:
    event = None

    if matches := RE_EVENT_D_MD.findall(line):
        event = parse_event_d_md_line(matches[0], date)

    elif matches := RE_EVENT_D_D.findall(line):
        event = parse_event_d_d_line(matches[0], date)

    elif matches := RE_EVENT_D.findall(line):
        event = parse_event_d_line(matches[0], date)

    elif matches := RE_MONTH.findall(line):
        date = parse_month_line(matches[0], date)

    return (event, date)


def parse(date: Date) -> list[Event]:
    content = web.get(EVENTS_URL)

    events = []
    for line in content.split('\n'):
        event, date = parse_line(remove_tags(line), date)
        if event:
            events.append(event)

    return events


def scrape(dry_run: bool):
    events = parse(dateutil.today_date())
    events_ical = generate_ical(events, dateutil.today_date())

    if not dry_run:
        with open('./docs/events.ical', 'w', encoding='utf-8') as f:
            f.write(events_ical)

    logger.success('the events was successfully updated.')
