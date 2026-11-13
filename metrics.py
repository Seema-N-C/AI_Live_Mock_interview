import re

FILLERS = ["um", "uh", "like", "basically", "you know", "actually"]


def analyze(text: str, segments: list) -> dict:
    words = text.split()
    n = max(len(words), 1)
    low = text.lower()
    fillers = sum(len(re.findall(rf"\b{re.escape(f)}\b", low)) for f in FILLERS)

    wpm = 0
    if segments:
        duration = segments[-1]["end"] - segments[0]["start"]
        wpm = round(n / max(duration, 1) * 60)

    pauses = sum(1 for a, b in zip(segments, segments[1:]) if b["start"] - a["end"] > 1.5)

    score = 10
    filler_rate = fillers / n * 100
    if filler_rate > 5:
        score -= 3
    elif filler_rate > 2:
        score -= 1
    if wpm and (wpm < 100 or wpm > 180):
        score -= 2
    if pauses > 3:
        score -= 2
    if n < 15:
        score -= 3

    return {"fillers": fillers, "wpm": wpm, "pauses": pauses,
            "words": n, "comm_score": max(score, 0)}
