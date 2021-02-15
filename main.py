import argparse
from scraping.scrapers import classes, events, news


def is_dry_run() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return args.dry_run


def main():
    dry_run = is_dry_run()
    classes.scrape(dry_run)
    events.scrape(dry_run)
    news.scrape(dry_run)


if __name__ == '__main__':
    main()
