from pathlib import Path

words = []

with open(Path("dictionary.txt").absolute()) as f:
    words = f.read().splitlines()
    f.close()


## TEST 1: LETTER DISTRIBUTION ##
dist = {}

for word in words:
    usedch = []
    for ch in word:
        if ch not in usedch:
            dist[ch] = dist.get(ch, 0) + 1
            usedch.append(ch)

for key in dist.keys():
    dist[key] = dist[key] / len(words)

print(dist)
