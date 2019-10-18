import db
import logger
from extractor.classextractor import ClassExtractor


def update_class():
    ce = ClassExtractor()
    class_infos = ce.extract_all()
    [add_class_to_db('classes', ci) for ci in class_infos]
    logger.info(f'{len(class_infos)} class changes updated.')


def add_class_to_db(col, ci):
    if not db.document_exists(col, ci.to_id()):
        db.set_value(col, ci.to_id(), ci.to_dict())
        logger.info(f'Added :{ci}')


def main():
    update_class()


if __name__ == '__main__':
    main()
