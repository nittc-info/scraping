import hashlib
from libs import logger
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
from libs.web import get_html_source


class NoticeExtractor:
    url = "http://www.tsuyama-ct.ac.jp"
    jst = timezone(timedelta(hours=+9), "JST")

    def create_feedgen(self) -> FeedGenerator:
        fg = FeedGenerator()
        fg.id(self.url)
        fg.title("津山高専からのお知らせ")
        return fg

    def parse(self, fg: FeedGenerator, html_source: str):
        soup = BeautifulSoup(html_source, "html.parser")
        notice_table = soup.find("table", class_="tabnews")

        if not notice_table:
            logger.failure("Can't find notice table.")
            return

        rows = notice_table.find_all("tr")
        for row in rows:
            self.parse_row(fg, row)

    def parse_row(self, fg: FeedGenerator, row):
        cols = row.find_all("td")
        if len(cols) != 3:
            return

        date_str = cols[0].text
        # 最下段
        if date_str == "--":
            return

        fe = fg.add_entry()

        updated_date = datetime.strptime(cols[0].text, "%Y.%m.%d")
        updated_date = updated_date.astimezone(self.jst)
        fe.updated(updated_date)

        kind = cols[1].text
        content = "".join([str(content) for content in cols[2].text])
        fe.title(f"[{kind}] {content}")

        fe.id(self.generate_id(content))
        fe.link(href=self.url)

    def generate_id(self, content: str) -> str:
        m = hashlib.md5()
        m.update(content.encode("utf-8"))
        return m.hexdigest()

    def extract(self) -> str:
        source = get_html_source(self.url)
        fg = self.create_feedgen()
        self.parse(fg, source)
        return fg.atom_str().decode("utf-8")
