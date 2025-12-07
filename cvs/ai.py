# cvs/ai.py
import requests
import json
import PyPDF2
import re
from django.conf import settings

SKILL_KEYWORDS = [
    # --- Ngôn ngữ lập trình ---
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Kotlin",
    "Swift", "PHP", "Ruby", "Scala", "Rust", "Perl", "MATLAB", "R",

    # --- Web Development ---
    "HTML", "CSS", "React", "Next.js", "NextJS", "Angular", "Vue.js", "Svelte",
    "Node.js", "NodeJS", "Express.js", "ExpressJS", "Django", "Flask", "FastAPI", "Spring Boot",
    "REST API", "GraphQL", "WebSocket", "Tailwind", "Bootstrap",

    # --- Mobile ---
    "Flutter", "React Native", "Android", "iOS", "SwiftUI", "Xamarin",

    # --- Data / AI / ML ---
    "Machine Learning", "Deep Learning", "Data Science", "Data Mining",
    "Data Visualization", "Natural Language Processing", "Computer Vision",
    "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "OpenCV",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "XGBoost", "LightGBM",
    "Học máy", "Trí tuệ nhân tạo", "AI", "Khoa học dữ liệu",
    "Phân tích dữ liệu", "Deep Learning", "Xử lý ngôn ngữ tự nhiên", "Thị giác máy tính",

    # --- Database ---
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    "Oracle", "Elasticsearch", "Firebase",

    # --- DevOps & Cloud ---
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Jenkins",
    "Git", "GitLab", "GitHub Actions", "Terraform", "Linux", "Ubuntu",
    "Shell Script", "Bash", "Nginx", "Apache",

    # --- Software Tools ---
    "Excel", "Power BI", "Tableau", "Jira", "Confluence", "Notion",
    "Slack", "Figma", "Adobe XD", "Photoshop", "Illustrator",

    # --- Testing & QA ---
    "Selenium", "Cypress", "Jest", "JUnit", "Postman", "Unit Test",
    "Integration Testing", "Automation Testing",

    # --- Soft Skills & Language ---
    "Communication", "Teamwork", "Leadership", "Problem Solving",
    "Time Management", "Agile", "Scrum", "Kanban",
    "English", "Japanese", "Korean", "Chinese", "Vietnamese",
    "Làm việc nhóm", "Giao tiếp", "Tư duy phản biện", "Lãnh đạo", "Quản lý thời gian",
    "Giải quyết vấn đề", "Học hỏi nhanh", "Thuyết trình", "Tiếng Anh", "Tiếng Nhật", "Tiếng Hàn",

    # --- Others ---
    "Blockchain", "Smart Contract", "Solidity", "Web3", "Metaverse",
    "3D Modeling", "Unity", "Unreal Engine"
]

def extract_text(file_path):
    """Đọc và trích xuất text từ file PDF"""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def analyze_cv(file_path):
    base_url = getattr(settings, "CV_API_BASE_URL", None)
    api_key = getattr(settings, "CV_API_KEY", None)

    if not base_url:
        raise ValueError("Thiếu CV_API_BASE_URL trong settings.py")
    
    cv_text = extract_text(file_path)
    if not cv_text.strip():
        return {"error": "CV không chứa nội dung văn bản (có thể là ảnh scan)."}

    prompt = f"""
    Phân tích nội dung CV dưới đây:
    ---
    {cv_text}
    ---
    Hãy tóm tắt thông tin cá nhân (tên, email, điện thoại),
    kỹ năng (skills), kinh nghiệm và học vấn.
    Trả kết quả theo JSON có cấu trúc:
    {{
        "full_name": "...",
        "email": "...",
        "phone": "...",
        "skills": ["..."],
        "education": "...",
        "experience": "..."
    }}
    """

    payload = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia tuyển dụng phân tích CV chuyên nghiệp."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(base_url, headers=headers, json=payload, timeout=60)

    if not response.ok:
        raise Exception(f"Lỗi API phân tích CV: {response.status_code} - {response.text}")

    result_text = response.json()["choices"][0]["message"]["content"]

    # Cố gắng parse JSON nếu model trả đúng định dạng
    data = safe_json_parse(result_text)
    if not data:
        print("⚠️ JSON lỗi, nội dung GPT trả về:")
        print(result_text)
        data = {"raw_output": result_text}

    # Chuẩn hóa thông tin để lưu vào DB
    return {
        "full_name": data.get("full_name") or data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "skills": ", ".join(data.get("skills", [])) if isinstance(data.get("skills"), list) else data.get("skills", ""),
        "education": "; ".join(data.get("education", [])) if isinstance(data.get("education"), list) else data.get("education", ""),
        "experience": "; ".join(data.get("experience", [])) if isinstance(data.get("experience"), list) else data.get("experience", ""),
        "extracted_text": cv_text
    }

def safe_json_parse(result_text):
    """Cố gắng parse JSON kể cả khi thiếu dấu phẩy hoặc ký tự thừa"""
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        # Thử tự động sửa lỗi phổ biến: thiếu dấu phẩy giữa chuỗi
        fixed = re.sub(r'"\s*"', '", "', result_text)
        try:
            return json.loads(fixed)
        except:
            return None
