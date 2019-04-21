import re, sys, os
import requests
import unicodedata
from datetime import datetime
from icalendar import Calendar, Event, vDate

RE_MONTH = re.compile(r"([０-９]+)月")
RE_DAY = re.compile(r"([０-９]+)日")

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


def zen_to_han_number(num):
	return int(unicodedata.normalize("NFKC", num))


def take_line_type(html_line):
	# 月を超えての行事に対応するためRE_DAYを先にする
	if RE_DAY.search(html_line): return 2
	if RE_MONTH.search(html_line): return 1
	return 0


def parse_event_line(html_line, cur_month):
	event = EventData()

	line = html_line.replace("<li>", "").replace("</li>", "")
	name = line.split("　")[-1]

	ryou = "寮"
	event_ryou = "【寮】"
	event_school = "【学校】"
	if ryou in name:
		event.subject = event_ryou + name
	else:
		event.subject = event_school + name

	day = RE_DAY.findall(line)
	month = RE_MONTH.findall(line)

	event.month_from = cur_month
	event.day_from = zen_to_han_number(day[0])

	if len(day) == 1:
		event.month_to = event.month_from
		event.day_to = event.day_from
	elif len(day) >= 2:
		if len(month) == 1:
			event.month_to = zen_to_han_number(month[0])
		else:
			event.month_to = cur_month
		event.day_from = zen_to_han_number(day[0])
		event.day_to = zen_to_han_number(day[1])
	else:
		print("Unable to parsing:" + line)
	return event


def parse_month_line(html_line):
	month = RE_MONTH.search(html_line).groups()[0]
	return zen_to_han_number(month)


def parse(url, now):
	r = requests.get(url)
	if r.status_code != 200:
		raise ConnectionError(f"Status Code:{r.status_code}")

	html_lines = r.content.decode("utf-8").split("\n")

	today_str = f"{now.year}.{now.month}.{now.day}"

	cal = Calendar()
	cal.add("prodid", f"津山高専行事予定{now.year}年度版（{today_str}時点）")
	cal.add("version", "2.0")

	is_next_year = False
	cur_month = 4
	for line in html_lines:
		line = line.strip().replace("  ", "")
		line_type = take_line_type(line)

		if line_type == 0:
			continue

		elif line_type == 1:
			cur_month = parse_month_line(line)
			is_next_year = cur_month <= 3

		elif line_type == 2:
			event_data = parse_event_line(line, cur_month)
			if is_next_year:
				event_data.year = now.year + 1
			else:
				event_data.year = now.year
			event_data.month_from = cur_month
			cal.add_component(event_data.to_ical_event())

	return cal.to_ical().decode("utf-8")

def start():
	import sys

	url = "http://www.tsuyama-ct.ac.jp/gyoujiVer4/gyouji.html"

	if len(sys.argv) != 2:
		print("Usage: calparse <outfile>")
		exit(0)

	now = datetime.today()

	output_file_name = "out/"  + sys.argv[1]

	if not os.path.exists("out"):
		os.mkdir("out")

	ical = parse(url, now)

	with open(output_file_name, "w", encoding="utf-8") as f:
		f.write(ical)

if __name__ == '__main__':
	start()