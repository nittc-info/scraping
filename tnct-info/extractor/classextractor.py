import re
from datetime import date
from libs.web import get_html_source, remove_tags
from model.classinfo import ClassInfo


class ClassExtractor:

    RE_CLASS_MD = re.compile(r"(\d+)月(\d+)日\(.\) ([A-Z0-9]+-[A-Z0-9]+) (.*)")

    def __init__(self):
        self.today = date.today()
        self.today_str = self.today.strftime('%Y%m%d')

    def get_matched_list(self, html_source: str) -> [re.Match]:
        return self.RE_CLASS_MD.findall(html_source)

    def parse_match_to_class(self, match: tuple) -> ClassInfo:
        class_info = ClassInfo()
        class_info.clazz = match[2]
        class_info.subject = remove_tags(match[3])
        class_info.date = date(self.today.year, int(match[0]), int(match[1])).strftime('%Y%m%d')
        class_info.published_date = self.today_str
        return class_info

    def extract(self, year: int, month: int) -> [ClassInfo]:
        url = f"http://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{year}{month:02}.html"
        source = get_html_source(url)
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
