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


def send_cv_email(to_email, cv_path, applicant_name, applicant_email):
    """Gửi email nộp CV cho nhà tuyển dụng"""
    subject = f"[Ứng viên mới] {applicant_name} - Nộp CV từ Smart Recruit"
    body = f"""
    Xin chào,

    Tôi là {applicant_name}.
    Tôi gửi kèm CV của mình để ứng tuyển công việc trên nền tảng Smart Recruit.
    Email liên hệ: {applicant_email or '(chưa cung cấp)'}.

    Trân trọng,
    Smart Recruit
    """

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[to_email],
    )

    email.attach_file(cv_path)
    email.send()
