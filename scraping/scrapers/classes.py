import json
from bs4 import BeautifulSoup
from dataclasses import asdict
from scraping.services import firestore, logger, http, date
from scraping.parser import classes
from scraping.models.classes import Classes

CLASS_URL_FORMAT = 'https://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{}.html'


def gen_class_id(c: dict) -> str:
    return '{}-{}-{}'.format(
        c['department_id'],
        c['grade'],
        c['class_id'],
    )


def gen_course_id(c: dict) -> str:
    return '{}-{}-{}'.format(
        c['date'],
        c['period']['begin'],
        c['period']['end'],
    )


def split_classes(item) -> dict:
    items = []
    for class_ in item.classes:
        new_item = asdict(item)
        del new_item['classes']
        new_item['class'] = asdict(class_)
        items.append(new_item)
    return items


def update(c: Classes):
    published_date = date.today_str()

    for change in c.changes:
        for new_change in split_classes(change):
            new_change['published_date'] = published_date

            change_id = '{}-{}'.format(
                gen_course_id(
                    (new_change['course_to'] + new_change['course_from'])[0]),
                gen_class_id(new_change['class']),
            )

            if firestore.add('changes', change_id, new_change):
                logger.info(f'add change: {change_id}')

    for supplement in c.supplements:
        for new_supplement in split_classes(supplement):
            new_supplement['published_date'] = published_date

            supplement_id = '{}-{}'.format(
                gen_course_id(new_supplement['course']),
                gen_class_id(new_supplement['class']),
            )

            if firestore.add('supplements', supplement_id, new_supplement):
                logger.info(f'add supplement: {supplement_id}')

    for cancellation in c.cancellations:
        for new_cancellation in split_classes(cancellation):
            new_cancellation['published_date'] = published_date

            cancellation_id = '{}-{}'.format(
                gen_course_id(new_cancellation['course']),
                gen_class_id(new_cancellation['class']),
            )

            if firestore.add('cancellations', cancellation_id, new_cancellation):
                logger.info(f'add cancellation: {cancellation_id}')


def parse_at(year: int, month: int) -> tuple[list, list, list]:
    page_id = f'{year}{month:02}'
    url = CLASS_URL_FORMAT.format(page_id)
    content = http.get(url)
    soup = BeautifulSoup(content, 'html.parser')

    changes = []
    if div_change := soup.find('div', id=f'{page_id}ju'):
        for p in div_change.find_all('p'):
            changes.append(classes.parse_change(p.text, year))

    supplements = []
    if div_supplements := soup.find('div', id=f'{page_id}ho'):
        for p in div_supplements.find_all('p'):
            supplements.append(classes.parse_supplement(p.text, year))

    cancellations = []
    if div_cancellations := soup.find('div', id=f'{page_id}kyu'):
        for p in div_cancellations.find_all('p'):
            cancellations.append(
                classes.parse_cancellation(p.text, year))

    return (changes, supplements, cancellations)


def parse() -> Classes:
    year, _, _ = date.today()

    classes = Classes()
    for month in range(1, 13):
        if 1 <= month <= 3:
            changes, supplements, cancellations = parse_at(year + 1, month)
        else:
            changes, supplements, cancellations = parse_at(year, month)

        classes.changes += changes
        classes.supplements += supplements
        classes.cancellations += cancellations

    return classes


def scrape(dry_run: bool):
    # 2020/01-03 => 2019/04-12 2020/01-03
    # 2020/04-12 => 2020/04-12 2021/01-03
    classes = parse()

    if not dry_run:
        with open('./docs/classes.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(asdict(classes), ensure_ascii=False))
        update(classes)

    logger.success('the classes was successfully updated.')
