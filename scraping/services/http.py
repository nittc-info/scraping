import requests
from scraping.services import logger


def get(url: str) -> str:
    logger.info('GET: ' + url)
    res = requests.get(url)
    if res.status_code != 200:
        logger.failure(f'{res.status_code}')
        return ''
    logger.success('200')
    return res.content.decode('utf-8')
