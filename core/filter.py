def filter_candidate(experience: float, min_exp: float, score: int, threshold: int) -> str:
    if experience < min_exp:
        return "❌ Rejected"
    if score >= threshold:
        return "✅ Selected"
    elif 40 <= score < threshold:
        return "❓ Doubt"
    else:
        return "❌ Rejected"