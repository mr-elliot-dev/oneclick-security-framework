def score_url(indicators):
    """Deterministic heuristic score 0-100; not a malware verdict."""
    score = min(100, sum(int(x.get("weight", 0)) for x in indicators))
    if score >= 70: level = "high"
    elif score >= 40: level = "medium"
    elif score >= 15: level = "low"
    else: level = "informational"
    return {"score": score, "level": level, "note": "Heuristic score; validate findings manually."}
