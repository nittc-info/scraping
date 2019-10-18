import re
import logger
import requests
from datetime import date
from model.classinfo import ClassInfo


class ClassExtractor:

    def __init__(self):
        self.RE_CLASS_MD = re.compile(r"(\d+)月(\d+)日\(.\) ([A-Z0-9]+-[A-Z0-9]+) (.*)")
        self.today = date.today()
        self.today_str = self.today.strftime('%Y%m%d')

    def get_html_source(self, url: str) -> str:
        logger.info("GET: " + url)
        res = requests.get(url)
        if res.status_code != 200:
            logger.failure(f'{res.status_code}')
            return ""
        logger.success("200 OK")
        return res.content.decode("utf-8")

    def get_matched_list(self, html_source: str) -> [re.Match]:
        return self.RE_CLASS_MD.findall(html_source)

    def remove_tags(self, value: str):
        return re.sub('<[^>]*>', '', value)

    def parse_match_to_class(self, match: tuple) -> ClassInfo:
        class_info = ClassInfo()
        class_info.clazz = match[2]
        class_info.subject = self.remove_tags(match[3])
        class_info.date = date(self.today.year, int(match[0]), int(match[1])).strftime('%Y%m%d')
        class_info.published_date = self.today_str
        return class_info

    def extract(self, year: int, month: int) -> [ClassInfo]:
        url = f"http://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{year}{month:02}.html"
        source = self.get_html_source(url)
        matched = self.get_matched_list(source)
        class_infos = [self.parse_match_to_class(m) for m in matched]
        return class_infos

    def extract_all(self) -> [ClassInfo]:
        class_infos = []
        for m in range(1, 13):
            if 1 <= m <= 3:
                class_infos.extend(self.extract(self.today.year + 1, m))
            else:
                class_infos.extend(self.extract(self.today.year, m))
        return class_infos
