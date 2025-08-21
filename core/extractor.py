import re
import datetime

def extract_name(text: str) -> str:
    # Naive approach: first non-empty line
    for line in text.split("\n"):
        if line.strip():
            return line.strip()
    return "Unknown"

def extract_experience(text: str) -> float:
    """
    Extract experience only from 'Experience' or 'Work' sections
    (avoid 'Education' dates).
    """
    exp_text = ""
    # Narrow text to EXPERIENCE/WORK HISTORY section
    match = re.search(r"(experience|work history)(.*)", text, re.IGNORECASE | re.DOTALL)
    if match:
        exp_text = match.group(2)
    else:
        exp_text = text  # fallback

    # Regex for date ranges like "Jan 2018 - Dec 2020" or "Feb 2021 – Present"
    pattern = r"(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present)"
    matches = re.findall(pattern, exp_text)

    total_months = 0
    for start, end in matches:
        try:
            start_date = datetime.datetime.strptime(start, "%b %Y")
            end_date = datetime.datetime.today() if "Present" in end else datetime.datetime.strptime(end, "%b %Y")
            diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if diff > 0:
                total_months += diff
        except Exception:
            continue

    return round(total_months / 12, 1)

def extract_skills(text: str, skills_config: dict) -> dict:
    found = {}
    for skill, weight in skills_config.items():
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found[skill] = weight
    return found