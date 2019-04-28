import re, sys, os
import requests
import unicodedata
from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event, vDate

RE_MONTH = re.compile(r'＜([０-９]+)月＞')
RE_EVENT_D = re.compile(r"([０-９]+)日（.）")
RE_EVENT_D_D = re.compile(r"([０-９]+)日（.）～([０-９]+)日（.）")
RE_EVENT_D_MD = re.compile(r"([０-９]+)日（.）～([０-９]+)月([０-９]+)日（.）")

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
	if RE_EVENT_D_MD.search(html_line): return 4
	if RE_EVENT_D_D.search(html_line): return 3
	if RE_EVENT_D.search(html_line): return 2
	if RE_MONTH.search(html_line): return 1	
	return 0


def remove_garbage(line):
	# インデントを除去
	line = line.replace("  ", "")

	# タグを除去
	line = line.replace("<li>", "")
	line = line.replace("</li>", "")

	return line


def add_type(subject):
	ryou = "寮"
	event_ryou = "【寮】"
	event_school = "【学校】"
	if ryou in subject:
		return event_ryou + subject
	else:
		return event_school + subject


def parse_month_line(line):
	month = RE_MONTH.search(line)
	return z2h(month.group(1))


def parse_day_event(line):
	day = RE_EVENT_D.search(line)
	return z2h(day.group(1))


def parse_span_event_d(line):
	day = RE_EVENT_D_D.search(line)
	return (z2h(day.group(1)), z2h(day.group(2)))


def parse_span_event_md(line):
	day = RE_EVENT_D_MD.search(line)
	return (z2h(day.group(1)), z2h(day.group(2)), z2h(day.group(3)))


def parse(url, now):
	r = requests.get(url)
	if r.status_code != 200:
		raise ConnectionError(f"Status Code:{r.status_code}")

	html_lines = r.content.decode("utf-8").split("\n")

	today_str = f"{now.year}.{now.month}.{now.day}"

	cal = Calendar()
	cal.add("prodid", f"津山高専行事予定{now.year}年度版（{today_str}時点）")
	cal.add("version", "2.0")

	cur_year = now.year
	cur_month = 4
	for line in html_lines:
		line = remove_garbage(line.strip())

		event = EventData()
		event.year = cur_year

		subject = add_type(line.split("　")[-1])
		event.subject = subject

		line_type = get_line_type(line)
		if line_type == 0:
			# 予定に関係ない
			continue

		elif line_type == 1:
			# 月表示
			cur_month = parse_month_line(line)
			if cur_month >= 1 and cur_month <= 3:
				cur_year = now.year + 1
			else:
				cur_year = now.year
			continue

		elif line_type == 2:
			# 一日のみの予定
			day = parse_day_event(line)
			event.month_from = event.month_to = cur_month
			event.day_from = event.day_to = day

		elif line_type == 3:
			# 期間予定（日〜日）
			day_from, day_to = parse_span_event_d(line)
			event.month_from = event.month_to = cur_month
			event.day_from, event.day_to = day_from, day_to

		elif line_type == 4:
			# 期間予定（日〜月日）
			day_from, month_to, day_to = parse_span_event_md(line)
			event.month_from, event.month_to = cur_month, month_to
			event.day_from, event.day_to = day_from, day_to

		cal.add_component(event.to_ical_event())

	return cal.to_ical().decode("utf-8")

def start():
	import sys

	url = "http://www.tsuyama-ct.ac.jp/gyoujiVer4/gyouji.html"

	if len(sys.argv) != 2:
		print("Usage: calparse <outfile>")
		exit(0)

	jst = timezone(timedelta(hours=+9), 'JST')

	now = datetime.now(jst)

	output_file_name = "out/"  + sys.argv[1]

	if not os.path.exists("out"):
		os.mkdir("out")

	ical = parse(url, now)

	with open(output_file_name, "w", encoding="utf-8") as f:
		f.write(ical)

if __name__ == '__main__':
	start()