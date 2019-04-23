import re
import json
import utils
import requests
import datetime
from bs4 import BeautifulSoup as BS
from datetime import datetime, timezone, timedelta

def replace_link(text):
	text = text.replace('<a href="', '')
	text = text.replace('</a>', '>')
	text = text.replace('">', '|')
	return text

def parse(url, today_str):
	r = requests.get(url)
	if r.status_code != 200:
		raise ConnectionError(f"Status Code:{r.status_code}")

	soup = BS(r.content, "html.parser")
	table = soup.find("table", class_ = "tabnews")

	if not table:
		print("Can't find news table.")
		exit(1)
	
	notices = []

	for row in table.find_all("tr"):
		datas = row.find_all("td")
		if len(datas) != 3:
			continue
		date = datas[0].text
		if date != today_str:
			continue
		kind = datas[1].text
		content = "".join([str(content) for content in datas[2].contents])
		content = "<" + url + replace_link(content)
		notices.append(f"[{kind}] {content}")
	return notices

def start():
	url = "http://www.tsuyama-ct.ac.jp/"

	jst = timezone(timedelta(hours=+9), 'JST')

	now = datetime.now(jst)
	today_str = f"{now.year}.{now.month}.{now.day}"

	notices = parse(url, today_str)
	if len(notices) != 0:
		message = "\n".join(notices)
		utils.post(message)
	exit(0)


if __name__ == "__main__":
	start()



