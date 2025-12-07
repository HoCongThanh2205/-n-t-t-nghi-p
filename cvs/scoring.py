import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def calculate_tfidf_similarity(text1, text2):
    """
    Tính độ tương đồng Cosine giữa 2 văn bản dùng TF-IDF.
    Trả về giá trị từ 0.0 đến 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        # Tạo corpus gồm 2 văn bản
        corpus = [text1, text2]
        
        # Khởi tạo vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Fit và transform
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Tính cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        return similarity[0][0]
    except Exception as e:
        print(f"Lỗi tính TF-IDF: {e}")
        return 0.0

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

    # --- 2️⃣ Đếm kỹ năng trùng (Skill Match) ---
    skill_match_score = 0
    if job_labels and cv_skills:
        matched = [s for s in cv_skills if s in job_labels]
        match_ratio = len(matched) / len(job_labels)
        skill_match_score = min(match_ratio * 100, 100)

    # --- 3️⃣ Tính độ tương đồng ngữ nghĩa (Semantic Match) ---
    # Lấy full text từ CV (nếu có) hoặc ghép các trường lại
    cv_full_text = cv_data.get("extracted_text", "")
    if not cv_full_text:
        # Fallback: ghép các trường quan trọng
        parts = [
            cv_data.get("skills", ""),
            cv_data.get("experience", ""),
            cv_data.get("education", "")
        ]
        cv_full_text = " ".join([str(p) for p in parts if p])

    # Lấy full text từ Job
    job_full_text = f"{job.title} {job.description or ''} {job.labels or ''}"

    semantic_score = calculate_tfidf_similarity(cv_full_text, job_full_text) * 100

    # --- 4️⃣ Tổng hợp điểm ---
    # Trọng số: 50% Skill Match + 50% Semantic Match
    # Nếu không có skill match (VD: job không có label), dùng 100% semantic
    
    if not job_labels:
        final_score = semantic_score
    else:
        final_score = (skill_match_score * 0.5) + (semantic_score * 0.5)

    # Bonus điểm nếu có từ khóa trong kinh nghiệm (giữ lại logic cũ nhưng giảm trọng số)
    exp_text = (cv_data.get("experience") or "").lower()
    bonus = 0
    if job_labels:
        matched = [s for s in cv_skills if s in job_labels]
        for lbl in matched:
            if lbl in exp_text:
                bonus += 2 

    bonus = min(bonus, 10)
    total_score = min(final_score + bonus, 100)

    return round(total_score, 2)
