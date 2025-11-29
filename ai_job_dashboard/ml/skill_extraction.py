import re
from typing import List
from ai_job_dashboard.utils.logger import get_logger
logger = get_logger("SkillExtraction")

# small dictionary you can expand with thousands of skills
SKILL_DICTIONARY = [
    "python","sql","tensorflow","pytorch","spark","hadoop","aws","azure","gcp","pandas","numpy",
    "scikit-learn","docker","kubernetes","git","excel","power bi","tableau","nlp","computer vision",
    "deep learning","machine learning","javascript","react","java"
]

def extract_skills_from_text(text: str, expand_dictionary=None) -> List[str]:
    text_lower = (text or "").lower()
    found = set()
    dic = (SKILL_DICTIONARY + (expand_dictionary or []))
    for skill in dic:
        # match whole words and common variations
        skill_esc = re.escape(skill.lower())
        pattern = r'\\b' + skill_esc + r's?\\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(list(found))
