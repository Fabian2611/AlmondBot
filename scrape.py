from pathlib import Path

def get_distribution(words: list[str]) -> dict:
    dist = {}

    for word in words:
        usedch = []
        for ch in word:
            if ch not in usedch:
                dist[ch] = dist.get(ch, 0) + 1
                usedch.append(ch)

    for key in dist.keys():
        dist[key] = dist[key] / len(words)

    return dist