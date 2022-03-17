import subprocess
import itertools
from log_manager import logger

unicodes = [
    {"\u0430": "Cyrillic Small Letter A"},
    {"\u03F2": "Greek Lunate Sigma Symbol"},
    {"\u0435": "Cyrillic Small Letter Ie"},
    {"\u043E": "Cyrillic Small Letter O"},
    {"\u0440": "Cyrillic Small Letter Er"},
    {"\u0455": "Cyrillic Small Letter Dze"},
    {"\u0501": "Cyrillic Small Letter Komi De"},
    {"\u051B": "Cyrillic Small Letter Qa"},
    {"\u051D": "Cyrillic Small Letter We"},
]

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


def generate_homoglyphs(url: str) -> str:
    url = url.lower()

    e_matchs = [list(em)[0] for em in evils if list(em)[0].upper() in url.upper()]

    cst = "".join(list(ch)[0] for ch in e_matchs)
    words = []
    for i in range(1, 9):
        words.extend("".join(j) for j in itertools.combinations(cst, i))
    for word in words:
        newurl = url
        unicd = []
        name = []
        chars = []
        for w in word:
            for em in evils:
                if list(em)[0] == w:
                    chr = em[list(em)[0]]
                    unicd.append(chr)
                    chars.append(w)
                    name.extend(u[chr] for u in unicodes if list(u)[0] == chr)
                    newurl = newurl.replace(w, chr)
                    logger.debug(f"Unicd: {unicd} chars: {chars} name: {name}")
                    return newurl
