from typing import List, Dict
from src.nlp.skill_extraction import SKILL_DICTIONARY, extract_skills_from_text

def skill_gap(resume_text: str, target_job_text: str, expand_dictionary=None):
    resume_skills = set(extract_skills_from_text(resume_text, expand_dictionary))
    job_skills = set(extract_skills_from_text(target_job_text, expand_dictionary))
    missing = sorted(list(job_skills - resume_skills))
    extra = sorted(list(resume_skills - job_skills))
    return {"missing": missing, "extra": extra, "job_skills": sorted(list(job_skills)), "resume_skills": sorted(list(resume_skills))}
