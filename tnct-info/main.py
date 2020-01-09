import argparse
from libs import logger, db
from extractor.classextractor import ClassExtractor
from extractor.eventextractor import EventExtractor


def main():
    is_debug = is_debugging()
    update_class(is_debug)
    update_event(is_debug)


def is_debugging() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    return args.debug


def update_class(is_debug: bool):
    ce = ClassExtractor()
    class_infos = ce.extract_all()
    if not is_debug:
        [add_class_to_db('classes', ci) for ci in class_infos]
    logger.info(f'{len(class_infos)} class changes updated.')


def add_class_to_db(col, ci):
    if not db.document_exists(col, ci.to_id()):
        db.set_value(col, ci.to_id(), ci.to_dict())
        logger.info(f'Added :{ci}')


if __name__ == '__main__':
    main()
