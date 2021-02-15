import logging
import colorama
from colorama import Fore, Style

logger = logging.getLogger("scraping")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
logger.addHandler(handler)

colorama.init()

prefixes = {
    'status': '[' + Fore.MAGENTA + Style.BRIGHT + 'x' + Style.RESET_ALL + ']',
    'success': '[' + Fore.GREEN + Style.BRIGHT + '+' + Style.RESET_ALL + ']',
    'failure': '[' + Fore.RED + Style.BRIGHT + '-' + Style.RESET_ALL + ']',
    'info': '[' + Fore.BLUE + Style.BRIGHT + '*' + Style.RESET_ALL + ']',
    'warning': '[' + Fore.YELLOW + Style.BRIGHT + '!' + Style.RESET_ALL + ']',
}


def set_level(level):
    logger.setLevel(level)


def emmit(s: str, *args) -> None:
    logger.info(s, *args)


def status(s: str, *args) -> None:
    logger.info(prefixes['status'] + s, *args)


def success(s: str, *args) -> None:
    logger.info(prefixes['success'] + s, *args)


def failure(s: str, *args) -> None:
    logger.info(prefixes['failure'] + s, *args)


def info(s: str, *args) -> None:
    logger.info(prefixes['info'] + s, *args)


def warning(s: str, *args) -> None:
    logger.warning(prefixes['warning'] + s, *args)
