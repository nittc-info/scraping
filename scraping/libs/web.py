import re
from libs import logger
import requests


def get_html_source(url: str) -> str:
    logger.info("GET: " + url)
    res = requests.get(url)
    if res.status_code != 200:
        logger.failure(f'{res.status_code}')
        return ""
    logger.success("200 OK")
    return res.content.decode("utf-8")


def remove_tags(value: str):
    value = value.replace("  ", "")
    return re.sub('<[^>]*>', '', value)
