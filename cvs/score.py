# cvs/score.py
import re

def normalize_skill(skill):
    """Chuẩn hóa kỹ năng: bỏ khoảng trắng, viết thường."""
    return re.sub(r"\s+", " ", skill.strip().lower())

def score_cv_vs_job(cv_skills, job_skills):
    """
    Tính điểm phù hợp giữa kỹ năng CV và công việc.
    Trả về tuple: (điểm %, danh sách kỹ năng trùng)
    """
    if not cv_skills or not job_skills:
        return 0, []

    # chuẩn hóa và tách từ
    cv_set = set(map(normalize_skill, re.split(r"[,;]", cv_skills)))
    job_set = set(map(normalize_skill, re.split(r"[,;]", job_skills)))

    matched = cv_set & job_set
    score = int(len(matched) / len(job_set) * 100) if job_set else 0

    return score, sorted(matched)
