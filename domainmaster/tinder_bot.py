from log_manager import logger

import subprocess
import itertools

evils = [
    {"a": "\u0430"},
    {"c": "\u03F2"},
    {"e": "\u0435"},
    {"o": "\u043E"},
    {"p": "\u0440"},
    {"s": "\u0455"},
    {"d": "\u0501"},
    {"q": "\u051B"},
    {"w": "\u051D"},
]


def generate_homoglyphs(url: str) -> list:
    url = url.lower()
    homoglyphs = []

    for i, e in itertools.product(range(len(url)), evils):
        letter, evil = list(e.items())[0]
        if letter == url[i]:
            homoglyphs.append(url[:i] + evil + url[i + 1 :])
    for homoglyph in homoglyphs:
        homoglyphs.extend(generate_homoglyphs(homoglyph))
    return list(dict.fromkeys(homoglyphs))


r = generate_homoglyphs("peace")
print(r)
