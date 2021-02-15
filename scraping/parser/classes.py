from scraping.models.classes import Change, Supplement, Cancellation, Class, Period, Course
from lark import Lark

parser_change = Lark.open(
    'scraping/parser/classes.lark',
    start='change'
)

parser_supplement = Lark.open(
    'scraping/parser/classes.lark',
    start='supplement'
)

parser_cancellation = Lark.open(
    'scraping/parser/classes.lark',
    start='cancellation'
)


def parse_change(s: str, year: int) -> Change:
    return walk_change(parser_change.parse(s), year)


def walk_change(t, year: int) -> Change:
    c = Change()
    arrow = None

    if t.data == 'change_1':
        date = walk_date(t.children[0], year)
        c.classes = walk_class(t.children[1])
        c.course_to, c.notes = walk_course(t.children[2], year)

    elif t.data == 'change_2':
        date = walk_date(t.children[0], year)
        c.classes = walk_class(t.children[1])
        c.course_from, notes_from = walk_course(t.children[2], year)
        c.course_to, notes_to = walk_course(t.children[4], year)
        c.notes = notes_from + notes_to
        arrow = t.children[3]

    elif t.data == 'change_3':
        date = walk_date(t.children[0], year)
        c.classes = walk_class(t.children[1])
        c.course_to, c.notes = walk_course(t.children[4], year)
        for i in range(len(c.course_to)):
            c.course_to[i].period = walk_period(t.children[2])
        arrow = t.children[3]

    elif t.data == 'change_4':
        date = walk_date(t.children[0], year)
        c.classes = walk_class(t.children[1])
        c.course_from, c.notes = walk_course(t.children[2], year)
        notes = []
        for note in t.children[4:]:
            notes.append(walk_note(note))
        c.notes += notes
        arrow = t.children[3]

    if arrow is not None and str(arrow.children[0]) == '←':
        c.course_from, c.course_to = c.course_to, c.course_from

    return normalize_change(c, date)


def normalize_change(c: Change, date: str) -> Change:
    for i in range(len(c.course_from)):
        i_to = min(i, len(c.course_to) - 1)
        if c.course_from[i].date == '':
            c.course_from[i].date = date
        if c.course_from[i].name == '':
            c.course_from[i].name = c.course_to[i_to].name
            if c.course_from[i].instructor == '':
                c.course_from[i].instructor = c.course_to[i_to].instructor

    for i in range(len(c.course_to)):
        i_from = min(i, len(c.course_from) - 1)
        if c.course_to[i].date == '':
            c.course_to[i].date = date
        if c.course_to[i].period is None:
            c.course_to[i].period = c.course_from[i_from].period
        if c.course_to[i].name == '':
            c.course_to[i].name = c.course_from[i_from].name
            if c.course_to[i].instructor == '':
                c.course_to[i].instructor = c.course_from[i_from].instructor

    return c


def parse_supplement(line: str, year: int) -> Supplement:
    return walk_supplement(parser_supplement.parse(line), year)


def walk_supplement(t, year: int) -> Supplement:
    s = Supplement()

    s.date = walk_date(t.children[0], year)
    s.classes = walk_class(t.children[1])
    courses, s.notes = walk_course(t.children[2], year)
    s.course = courses[0]

    s.course.date = s.date

    return s


def parse_cancellation(line: str, year: int) -> Cancellation:
    return walk_cancellation(parser_cancellation.parse(line), year)


def walk_cancellation(t, year: int) -> Cancellation:
    c = Cancellation()

    c.date = walk_date(t.children[0], year)
    c.classes = walk_class(t.children[1])
    courses, c.notes = walk_course(t.children[2], year)
    c.course = courses[0]

    c.course.date = c.date

    return c


# TODO
def walk_date(t, year: int) -> str:
    if t.data == 'date':
        month, day, _ = t.children
        return f'{year}-{int(month):02}-{int(day):02}'

    elif t.data == 'date_after':
        month, day, _ = t.children
        return f'after-{year}-{int(month):02}-{int(day):02}'

    elif t.data == 'date_first_term':
        return f'{year}-1h'


def walk_class(t) -> list[Class]:
    classes = []
    if t.data == 'class_1':
        classes.extend(walk_class_inner(t.children[0]))

    elif t.data == 'class_2':
        for class_ in t.children:
            classes.extend(walk_class_inner(class_))

    return classes


DEPARTMENTS = {
    'S': 1,
    'M': 2,
    'E': 3,
    'C': 4,
}

DEPARTMENTS_ADV = {
    'MS': 1,
    'EC': 2,
}


def walk_class_inner(t) -> list[Class]:
    c = Class()

    if t.data == 'class_inner_first':
        c.department_id = 1
        c.grade = int(t.children[0])
        c.class_id = int(t.children[1])

    elif t.data == 'class_inner_course':
        c.department_id = 1
        c.grade = int(t.children[0])
        if c.grade == 1:
            c.class_id = int(t.children[1])
        else:
            c.class_id = DEPARTMENTS[str(t.children[1])]

    elif t.data == 'class_inner_multiple_courses':
        classes = []
        for class_ in str(t.children[1]):
            c = Class()
            c.department_id = 1
            c.grade = int(t.children[0])
            c.class_id = DEPARTMENTS[class_]
            classes.append(c)
        return classes

    elif t.data == 'class_inner_dept':
        c.department_id = DEPARTMENTS[str(t.children[0])] + 2
        c.grade = int(t.children[1])

    elif t.data == 'class_inner_adv':
        c.department_id = 2
        c.grade = int(t.children[0])

    elif t.data == 'class_inner_adv_dept':
        c.department_id = 2
        c.grade = int(t.children[1])
        c.class_id = DEPARTMENTS_ADV[str(t.children[0])]

    elif t.data == 'class_inner_inter_all':
        classes = []
        for class_id in range(1, 5):
            c = Class()
            c.department_id = 1
            c.grade = int(t.children[0])
            c.class_id = class_id
            c.international_student = True
            classes.append(c)
        return classes

    elif t.data == 'class_inner_inter':
        classes = walk_class(t.children[0])
        for i in range(len(classes)):
            classes[i].international_student = True
        return classes

    elif t.data == 'class_inner_all':
        classes = []
        for class_id in range(1, 5):
            c.department_id = 1
            c.grade = int(t.children[0])
            c.class_id = class_id
        return classes

    elif t.data == 'class_inner_select':
        # TODO
        c.department_id = 1
        c.grade = int(t.children[0])
        c.note = '選択'

    return [c]


def walk_course(t, year: int) -> (list[Course], list[str]):
    if t.data == 'course_1':
        course, notes = walk_course_inner(t.children[0], year)
        return ([course], notes)

    elif t.data == 'course_2':
        course1, notes1 = walk_course_inner(t.children[0], year)
        course2, notes2 = walk_course_inner(t.children[1], year)
        return ([course1, course2], notes1 + notes2)


def walk_course_inner(t, year: int) -> (Course, list[str]):
    c = Course()
    notes = []

    for child in t.children:
        if child.data == 'date':
            c.date = walk_date(child, year)

        elif child.data.startswith('period_'):
            c.period = walk_period(child)

        elif child.data.startswith('course_name'):
            c.name = walk_course_name(child)

        elif child.data.startswith('instructor_'):
            c.instructor = walk_instructor(child)

        elif child.data == 'note':
            notes.append(walk_note(child))

    return (c, notes)


def walk_period(t) -> Period:
    p = Period()

    if t.data == 'period_1':
        p.begin = p.end = int(t.children[0])

    elif t.data == 'period_2':
        p.begin = int(t.children[0])
        p.end = int(t.children[1])

    elif t.data == 'period_3':
        # TODO
        pass

    return p


def walk_course_name(t) -> str:
    if t.data == 'course_name_default':
        return str(t.children[0])

    elif t.data == 'course_name_applicant':
        return str(t.children[0]) + '（希望者）'


def walk_instructor(t) -> str:
    if t.data == 'instructor_1':
        return str(t.children[0])

    elif t.data == 'instructor_2':
        return '{} {}'.format(t.children[0], t.children[1])


def walk_note(t) -> str:
    return str(t.children[0])
