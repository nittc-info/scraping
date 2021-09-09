from os import closerange
import re
import json
from bs4 import BeautifulSoup
from dataclasses import asdict
from scraping.services import firestore, logger, web, dateutil, twitter
from scraping.models.classes import ClassChange, ChangeType, class_id, class_to_dict

CLASS_URL_FORMAT = 'https://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{}.html'

RE_CLASS_MD = re.compile(r"(\d+)月(\d+)日")

HEADERS = ["授業変更", "補講", "休講"]
MAX_LETTERS = 140


def format_for_twitter(title: str, classes: list[ClassChange]) -> list[str]:
    tweets = []
    tweet = title + "\n"

    current_type = -1
    for c in sorted(classes, key=lambda c: c.type.value):
        if c.type.value != current_type:
            current_type = c.type.value
            tweet += HEADERS[current_type] + "\n"
        line = c.subject + "\n"
        if len(tweet) + len(line) >= MAX_LETTERS:
            tweets.append(tweet)
            tweet = HEADERS[current_type] + "\n"
        tweet += line
    tweets.append(tweet)
    return tweets


def update_today(classes: list[ClassChange]):
    logger.info("update_today")
    today = dateutil.today_str()
    classes_to_tweet = filter(lambda c: c.date == today, classes)
    logger.info(str(list(classes_to_tweet)))
    if not classes_to_tweet:
        return
    tweets = format_for_twitter("連絡事項（今日）", classes_to_tweet)
    for tweet in tweets:
        twitter.tweet(tweet)


def update_published(classes: list[ClassChange]):
    logger.info("update_published")
    classes_to_tweet = []
    for c in classes:
        c_id = class_id(c)
        c_dict = class_to_dict(c)
        if firestore.add('classes', c_id, c_dict):
            classes_to_tweet.append(c)

    logger.info(str(classes_to_tweet))
    if not classes_to_tweet:
        return
    tweets = format_for_twitter("連絡事項（追加）", classes_to_tweet)
    for tweet in tweets:
        twitter.tweet(tweet)


def parse_at(year: int, month: int) -> list[ClassChange]:
    page_id = f'{year}{month:02}'
    url = CLASS_URL_FORMAT.format(page_id)
    content = web.get(url)
    soup = BeautifulSoup(content, 'html.parser')

    lines = []
    if div := soup.find('div', id=f'{page_id}ju'):
        lines.extend([(p.text, ChangeType.Change) for p in div.find_all('p')])
    if div := soup.find('div', id=f'{page_id}ho'):
        lines.extend([(p.text, ChangeType.Supplement)
                     for p in div.find_all('p')])
    if div := soup.find('div', id=f'{page_id}kyu'):
        lines.extend([(p.text, ChangeType.Cancellation)
                     for p in div.find_all('p')])

    classes = []
    published_date = dateutil.today_str()
    for line, type in lines:
        matches = RE_CLASS_MD.findall(line)
        if len(matches) == 0:
            logger.warning(f"date not found: `{line}`")
            continue
        month, day = matches[0]
        date = f"{year:04}{int(month):02}{int(day):02}"
        classes.append(ClassChange(type, line, published_date, date))

    return classes


def parse() -> list[ClassChange]:
    year, _, _ = dateutil.today()

    classes = []
    for month in range(1, 13):
        if 1 <= month <= 3:
            classes_month = parse_at(year + 1, month)
        else:
            classes_month = parse_at(year, month)

        classes += classes_month

    return classes


def scrape(dry_run: bool):
    # 2020/01-03 => 2019/04-12 2020/01-03
    # 2020/04-12 => 2020/04-12 2021/01-03
    classes = parse()

    if not dry_run:
        update_published(classes)
        update_today(classes)

    logger.success('the classes was successfully updated.')
