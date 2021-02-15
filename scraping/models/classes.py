from dataclasses import dataclass, field


@dataclass
class Period:
    begin: int = 0
    end: int = 0


@dataclass
class Class:
    department_id: int = 0
    grade: int = 0
    class_id: int = 0
    international_student: bool = False
    note: str = ''


@dataclass
class Course:
    date: str = ''
    period: Period = None
    name: str = ''
    instructor: str = ''


@dataclass
class Change:
    classes: list[Class] = field(default_factory=list)
    course_from: list[Course] = field(default_factory=list)
    course_to: list[Course] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Supplement:
    classes: list[Class] = field(default_factory=list)
    course: Course = None
    notes: list[str] = field(default_factory=list)


@dataclass
class Cancellation:
    classes: list[Class] = field(default_factory=list)
    course: Course = None
    notes: list[str] = field(default_factory=list)


@dataclass
class Classes:
    changes: list[Change] = field(default_factory=list)
    supplements: list[Supplement] = field(default_factory=list)
    cancellations: list[Cancellation] = field(default_factory=list)
