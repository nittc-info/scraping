import requests, json

TOKEN = open("./secret", "r", encoding="utf-8").readline().strip()
WEB_HOOK_URL = f"https://hooks.slack.com/services/{TOKEN}"

def post(text):
	r = requests.post(WEB_HOOK_URL, data = json.dumps({
		'text': text,
		'username': u'TNCT Notification',
		'link_names': 1
	}))
	if r.status_code != 200:
		print(f"Can't post a message:{r.status_code}")
