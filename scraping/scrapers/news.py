from bs4 import BeautifulSoup
from datetime import datetime
from feedgen.feed import FeedGenerator
from scraping.models.news import News
from scraping.services import web, logger
from scraping.services.dateutil import JST

NEWS_URL = 'https://www.tsuyama-ct.ac.jp/'


def parse() -> list[News]:
    content = web.get(NEWS_URL)
    soup = BeautifulSoup(content, 'html.parser')

    news = []

    table_tabnews = soup.find('table', class_='tabnews')
    rows = table_tabnews.find_all('tr')
    for row in rows:
        cols = row.find_all('td')

        # 日付
        date_str = cols[0].text
        if date_str == '--':
            break
        date = datetime.strptime(date_str, '%Y.%m.%d').astimezone(JST)

        # 種別
        kind = cols[1].text

        # 内容
        subject = cols[2].text

        # 内容に含まれるリンク
        link = ''
        if link_a := cols[2].find('a'):
            link = link_a.get('href')

        news.append(News(date, kind, subject, link))

    return news


def generate_rss(all_news: list[News]) -> str:
    date_now = datetime.now(JST)
    fg = FeedGenerator()
    fg.title('津山高専からのお知らせ')
    fg.description('津山高専からのお知らせ')
    fg.link(href=NEWS_URL, rel='alternate')
    fg.lastBuildDate(date_now)
    fg.language('ja')

    for news in all_news:
        fe = fg.add_entry()
        fe.title(f'[{news.kind}] {news.subject}')
        fe.link(href=f'{NEWS_URL}{news.link}')
        fe.pubDate(news.published_date)

    return fg.rss_str().decode('utf-8')


def scrape(dry_run: bool):
    news = parse()
    news_rss = generate_rss(news)

    if not dry_run:
        with open('./docs/news.xml', 'w', encoding='utf-8') as f:
            f.write(news_rss)

    logger.success('the news was successfully updated.')
