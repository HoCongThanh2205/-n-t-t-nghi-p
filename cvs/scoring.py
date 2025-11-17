import re

def score_cv(cv_data):
    """
    cv_data là dict gồm các trường:
    full_name, email, phone, skills, education, experience
    """
    score = 0
    details = {}

    # 🧍‍♂️ 1️⃣ Thông tin liên hệ (tối đa 20 điểm)
    contact_score = 0
    name = cv_data.get("full_name", "")
    email = cv_data.get("email", "")
    phone = cv_data.get("phone", "")

    if name and name.lower() != "không xác định":
        contact_score += 7
    if email and "@" in email:
        contact_score += 7
    if phone and any(ch.isdigit() for ch in phone):
        contact_score += 6

    details["contact"] = contact_score
    score += contact_score

    # 🧠 2️⃣ Kỹ năng (tối đa 25 điểm)
    skills = cv_data.get("skills", "")
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    # Loại bỏ trùng kỹ năng
    skills = list(dict.fromkeys(skills))
    skills_score = min(len(skills) * 2, 25)
    details["skills"] = skills_score
    score += skills_score

    # 🎓 3️⃣ Học vấn (tối đa 15 điểm)
    education = cv_data.get("education", "")
    edu_score = 0
    if education and education.lower() != "không xác định":
        edu_score = 15
    details["education"] = edu_score
    score += edu_score

    # 💼 4️⃣ Kinh nghiệm (tối đa 25 điểm)
    experience = cv_data.get("experience", "")
    exp_score = 0
    if experience and experience.lower() != "không xác định":
        exp_score = 25
    details["experience"] = exp_score
    score += exp_score

    # 📄 5️⃣ Cấu trúc & độ dài nội dung (tối đa 15 điểm)
    total_text = " ".join(str(v) for v in cv_data.values() if v)
    structure_score = min(len(total_text) // 50, 15)  # cứ 400 ký tự = +1 điểm
    details["structure"] = structure_score
    score += structure_score

    # ✅ Tổng hợp (giới hạn tối đa 100 điểm)
    total = min(score, 100)

    return {
        "total": total,
        "breakdown": details
    }

def match_cv_to_job(cv_data, job):
    # --- 1️⃣ Chuẩn hóa dữ liệu ---
    cv_skills = []
    job_labels = []

    # CV skills
    if isinstance(cv_data.get("skills"), str):
        cv_skills = [s.strip().lower() for s in cv_data["skills"].split(",") if s.strip()]
    elif isinstance(cv_data.get("skills"), list):
        cv_skills = [s.strip().lower() for s in cv_data["skills"]]

    # Job labels
    if isinstance(job.labels, str):
        job_labels = [s.strip().lower() for s in re.split(r",|\|", job.labels) if s.strip()]
    elif isinstance(job.labels, list):
        job_labels = [s.strip().lower() for s in job.labels]

    if not job_labels or not cv_skills:
        return 0  # Không có dữ liệu để so sánh

    # --- 2️⃣ Đếm kỹ năng trùng ---
    matched = [s for s in cv_skills if s in job_labels]
    match_ratio = len(matched) / len(job_labels)

    # --- 3️⃣ Điểm kỹ năng ---
    skill_score = round(match_ratio * 80, 2)  # chiếm 80% tổng điểm

    # --- 4️⃣ Bonus điểm nếu có từ khóa trong kinh nghiệm ---
    exp_text = (cv_data.get("experience") or "").lower()
    bonus = 0
    for lbl in matched:
        if lbl in exp_text:
            bonus += 3  # mỗi kỹ năng có trong kinh nghiệm cộng thêm 3 điểm

    bonus = min(bonus, 20)  # giới hạn 20 điểm bonus
    total_score = min(skill_score + bonus, 100)

    return round(total_score, 2)
