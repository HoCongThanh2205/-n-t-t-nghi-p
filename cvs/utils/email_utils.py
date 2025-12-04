# cvs/utils/email_utils.py
import re
from django.core.mail import EmailMessage

def extract_contact_info(text):
    """Trích xuất email và số điện thoại từ nội dung JD"""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(\+84|0)(\d{9,10})"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    email = emails[0] if emails else None
    phone = ''.join(phones[0]) if phones else None

    return email, phone


def send_cv_email(to_email, cv_path, applicant_name, applicant_email, job_title="Công việc", skills=None):
    """Gửi email nộp CV cho nhà tuyển dụng"""
    subject = f"[Ứng viên mới] {applicant_name} - Nộp CV từ Smart Recruit"

    skills_text = ""
    if skills:
        skills_text = f"- Kỹ năng nổi bật: {skills}"

    body = f"""
    Kính gửi Bộ phận Tuyển dụng,

    Hệ thống Smart Recruit xin trân trọng chuyển tiếp hồ sơ ứng tuyển của ứng viên:

    - Họ tên: {applicant_name}.
    - Ứng tuyển theo nhu cầu công việc: {job_title}.
    - Email liên hệ: {applicant_email or '(chưa cung cấp)'}.
    {skills_text}

    Hồ sơ chi tiết (CV) đã được đính kèm trong email này.

    Trân trọng,
    Đội ngũ Smart Recruit
    """

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[to_email],
    )

    email.attach_file(cv_path)
    email.send()
