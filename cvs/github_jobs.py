# cvs/github_jobs.py
import requests
from datetime import datetime
from .models import Job
from .ai import SKILL_KEYWORDS

def fetch_and_save_jobs():
    url = "https://api.github.com/repos/awesome-jobs/vietnam/issues"
    response = requests.get(url, timeout=10)
    data = response.json()

    for job in data[:20]:
        job_url = job.get("html_url")
        if not Job.objects.filter(url=job_url).exists():

            # --- Xử lý labels ---
            labels_list = [lbl.get("name", "") for lbl in job.get("labels", [])]

            # --- Lấy nội dung JD ---
            body = job.get("body", "")

            if not labels_list:  # Nếu job không có labels gốc
                found = [kw for kw in SKILL_KEYWORDS if kw.lower() in body.lower()]
                labels_list = found or ["Không có"]

            labels = ", ".join(labels_list)

            # --- Tạo Job ---
            Job.objects.create(
                title=job.get("title"),
                company=job.get("user", {}).get("login", "Không rõ"),
                url=job_url,
                labels=labels,
                description=body,
                created_at=datetime.fromisoformat(job.get("created_at").replace("Z", "+00:00"))
            )

    return Job.objects.all().order_by('-created_at')
