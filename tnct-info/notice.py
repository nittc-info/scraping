import re, os, json, sys
import utils
import hashlib
import requests
import datetime
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup as BS
from datetime import datetime, timezone, timedelta

def replace_link(text):
	text = text.replace("<a href='", '')
	text = text.replace('</a>', '>')
	text = text.replace("'>", '|')
	return text

def parse(url):
	r = requests.get(url)
	if r.status_code != 200:
		raise ConnectionError(f'Status Code:{r.status_code}')

	soup = BS(r.content, 'html.parser')
	table = soup.find('table', class_ = 'tabnews')

	if not table:
		print("Can't find news table.")
		exit(1)
	
	fg = FeedGenerator()
	fg.id(url)
	fg.title('津山高専からのお知らせ')

	jst = timezone(timedelta(hours=+9), 'JST')

	for row in table.find_all('tr'):
		datas = row.find_all('td')
		if len(datas) != 3:
			continue
		date_str = datas[0].text
		if date_str == "--":
			break
		kind = datas[1].text
		content = ''.join([str(content) for content in datas[2].contents])
		fe = fg.add_entry()
		date = date_str.split('.')
		fe.title(f'[{kind}] {content}')
		fe.id(hashlib.md5(f'[{kind}] {content}'.encode()).hexdigest())
		fe.updated(datetime(int(date[0]), int(date[1]), int(date[2]), tzinfo=jst))
		fe.link(href=url)
	return fg.atom_str()

def start():
	url = 'http://www.tsuyama-ct.ac.jp/'

	if len(sys.argv) != 2:
		print("Usage: notice <outfile>")
		exit(0)

	output_file_name = "out/"  + sys.argv[1]

	if not os.path.exists("out"):
		os.mkdir("out")
	
	notice_atom_str = parse(url)

	with open(output_file_name, "w", encoding="utf-8") as f:
		f.write(notice_atom_str.decode("utf-8"))


if __name__ == '__main__':
	start()



