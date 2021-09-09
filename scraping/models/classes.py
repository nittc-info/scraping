from enum import Enum
from hashlib import md5
from dataclasses import dataclass


class ChangeType(Enum):
    Change = 0
    Supplement = 1
    Cancellation = 2


@dataclass
class ClassChange:
    type: ChangeType
    subject: str
    published_date: str
    date: str


def class_id(c: ClassChange) -> str:
    return md5(c.subject.encode('utf-8')).hexdigest() + str(c.date)


def class_to_dict(c: ClassChange) -> object:
    return {
        'type': c.type.value,
        'subject': c.subject,
        'published_date': c.published_date,
        'date': c.date,
    }
