import re, sys, os
import requests
import unicodedata
from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event, vDate
import enum


RE_EVENT_MD = re.compile(r"([0-9]+)月([0-9]+)日\(.\) (.*)")
RE_EVENT_MD_MD = re.compile(r"([0-9]+)月([0-9]+)日\(.\)～ ([0-9]+)月([0-9]+)日\(.\) (.*)")

Events = enum.Enum("Events", "md md_md unknown")

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

	def to_string_fromdate(self):
		return f"{self.subject},{self.month_from}/{self.day_from}/{self.year},{self.month_to}/{self.day_to}/{self.year},TRUE"


def z2h(num):
	return int(unicodedata.normalize("NFKC", num))


def get_line_type(html_line):
	if RE_EVENT_MD_MD.search(html_line): return Events.md_md
	if RE_EVENT_MD.search(html_line): return Events.md
	return Events.unknown


def remove_garbage(line):
	# インデントを除去
	line = line.replace("  ", "")

	# タグを除去
	line = line.replace("<p>", "")
	line = line.replace("</p>", "")

	return line


def parse_md_event(line):
	event = RE_EVENT_MD.search(line)
	return (z2h(event.group(1)), z2h(event.group(2)), event.group(3))

def parse_md_md_event(line):
	event = RE_EVENT_MD_MD.search(line)
	return (z2h(event.group(1)), z2h(event.group(2)), z2h(event.group(3)), z2h(event.group(4)), event.group(5))


def parse(year, month, cal):
	url = f"http://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{year}{month:02}.html"

	r = requests.get(url)
	if r.status_code != 200:
		print(f"{url} is not found.")
		return cal

	html_lines = r.content.decode("utf-8").split("\n")

	for line in html_lines:
		line = remove_garbage(line.strip())

		event = EventData()
		event.year = year

		line_type = get_line_type(line)
		if line_type == Events.unknown:
			# 予定に関係ない
			continue

		elif line_type == Events.md:
			month, day, subject = parse_md_event(line)
			event.month_from, event.month_to = month, month
			event.day_from, event.day_to = day, day
			event.subject = subject

		elif line_type == Events.md_md:
			month_from, day_from, month_to, day_to, subject = parse_md_md_event(line)
			event.month_from, event.month_to = month_from, month_to
			event.day_from, event.day_to = day_from, day_to
			event.subject = subject

		cal.add_component(event.to_ical_event())

	return cal

def start():
	import sys

	if len(sys.argv) != 2:
		print("Usage: class <outfile>")
		exit(0)

	output_file_name = "out/"  + sys.argv[1]
	if not os.path.exists("out"):
		os.mkdir("out")

	jst = timezone(timedelta(hours=+9), 'JST')
	now = datetime.now(jst)
	today_str = f"{now.year}.{now.month}.{now.day}"

	cal = Calendar()
	cal.add("prodid", f"津山高専連絡事項{now.year}年度版（{today_str}時点）")
	cal.add("version", "2.0")

	for month in range(1, 12):
		if month <= 3:
			cal = parse(now.year + 1, month, cal)
		else:
			cal = parse(now.year, month, cal)
		
	ical = cal.to_ical().decode('utf-8')

	with open(output_file_name, "w", encoding="utf-8") as f:
		f.write(ical)

if __name__ == '__main__':
	start()