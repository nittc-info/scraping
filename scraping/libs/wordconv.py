from unicodedata import normalize


def z2h(s: str) -> int:
    return int(normalize('NFKC', s))
