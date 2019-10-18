from hashlib import md5


class ClassInfo:
    def __init__(self):
        self.clazz: str = ""
        self.subject: str = ""
        self.published_date: str = ""
        self.date: str = ""

    def to_id(self) -> str:
        return md5(self.subject.encode('utf-8')).hexdigest() + str(self.date)

    def to_dict(self) -> object:
        return {
            'class': self.clazz,
            'subject': self.subject,
            'published_date': self.published_date,
            'date': self.date
        }

    def __str__(self):
        return f"ClassInfo(class:{self.clazz} subject:{self.subject} pubdate:{self.published_date} date:{self.date})"
