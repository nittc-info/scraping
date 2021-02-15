from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class News:
    published_date: datetime
    kind: str
    subject: str
    link: str
