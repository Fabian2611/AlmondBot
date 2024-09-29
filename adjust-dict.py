from settings import SETTINGS
from pathlib import Path

def alphanumerical(word: str) -> str:
    return "".join([ch for ch in word if ch.isalnum()])

def adjust_dict():
    lines = []
    with open(Path(SETTINGS["dictionary"]).absolute(), "r") as f:
        lines = f.readlines()
        f.close()
    lines = list(set(lines))
    lines.sort()
    with open(Path(SETTINGS["dictionary"]).absolute(), "w") as f:
        for line in lines:
            f.write(alphanumerical(line.strip().upper()) + "\n")
        f.close()

adjust_dict()
