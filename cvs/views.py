# cvs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CVForm
from .models import CV, Job, CVJobMatch
from .ai import analyze_cv
from .github_jobs import fetch_and_save_jobs
from .scoring import score_cv, match_cv_to_job
from .utils.email_utils import extract_contact_info, send_cv_email

def upload_cv(request):
    if request.method == "POST":
        form = CVForm(request.POST, request.FILES)
        if form.is_valid():
            cv = form.save()
            result = analyze_cv(cv.file.path)

            for key, value in result.items():
                setattr(cv, key, value)
            cv.save()

            messages.success(request, "✅ CV đã được tải lên và phân tích thành công!")
        else:
            messages.error(request, "❌ Vui lòng chọn file hợp lệ trước khi nộp.")    
    return redirect("home")

def apply_job(request, cv_id, job_id):
    cv = get_object_or_404(CV, id=cv_id)
    job = get_object_or_404(Job, id=job_id)

    # 1️⃣ Trích xuất email và số điện thoại từ JD
    email, phone = extract_contact_info(job.description or "")

    print("📧 Email trích xuất:", email)
    print("📞 SĐT trích xuất:", phone)

    # 2️⃣ Nếu có email → gửi CV tự động
    if email:
        try:
            send_cv_email(
                to_email="thanhhc2205@gmail.com",
                # to_email=email,
                cv_path=cv.file.path,
                applicant_name=cv.full_name or "Ứng viên ẩn danh",
                applicant_email=cv.email,
                job_title=job.title,
                skills=cv.skills
            )
            messages.success(request, f"✅ Đã gửi CV đến {email} thành công!")
        except Exception as e:
            messages.error(request, f"❌ Lỗi khi gửi email: {str(e)}")

    # 3️⃣ Nếu không có email nhưng có số điện thoại
    elif phone:
        messages.warning(request, f"📞 Không tìm thấy email. Vui lòng liên hệ qua số: {phone}")

    # 4️⃣ Nếu không có cả 2
    else:
        messages.info(request, "⚠️ Không tìm thấy thông tin liên hệ trong JD.")

    return redirect("home")

def home(request):
    # --- 1️⃣ Biến mặc định ---
    form = CVForm()
    analyzed_data = None
    cv_score = None
    match_results = []
    current_cv = None

    # --- 2️⃣ Upload và phân tích CV ---
    if request.method == "POST":
        form = CVForm(request.POST, request.FILES)
        if form.is_valid():
            cv = form.save()
            current_cv = cv

            # 🔍 Phân tích CV bằng AI
            data = analyze_cv(cv.file.path)
            analyzed_data = data

            # 💾 Lưu thông tin phân tích vào DB
            for k, v in data.items():
                setattr(cv, k, v)

            # 📊 Tính điểm CV (score_cv trả dict: total + breakdown)
            cv_score_data = score_cv(data)
            cv_score_value = cv_score_data["total"]
            cv.score = cv_score_value
            cv_score = cv_score_data  # để hiển thị ra template

            # 🎯 Tính độ phù hợp với từng job
            # Lấy tất cả job để match
            all_jobs = Job.objects.all()
            matches = []
            
            # Xóa các match cũ của CV này (nếu muốn làm mới hoàn toàn)
            CVJobMatch.objects.filter(cv=cv).delete()

            for job in all_jobs:
                match_score = match_cv_to_job(analyzed_data, job)
                if match_score > 0:
                    # Lưu vào DB
                    CVJobMatch.objects.create(
                        cv=cv,
                        job=job,
                        match_score=match_score
                    )
                    matches.append({"job": job, "score": match_score})

            # 🔽 Sắp xếp theo độ phù hợp giảm dần
            matches.sort(key=lambda x: x["score"], reverse=True)
            match_results = matches[:3]  # top 3 gợi ý

            # ⚖️ Tính match score trung bình (cho ứng viên)
            match_scores = [m["score"] for m in matches]
            avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
            cv.match_score = round(avg_match_score, 2)

            # 🌟 Tính điểm tiềm năng tổng hợp
            cv.potential_score = round((cv.score * 0.6) + (cv.match_score * 0.4), 2)

            # 💾 Lưu tất cả vào DB
            cv.save()

            messages.success(request, "✅ CV đã được phân tích và tính điểm thành công!")
        else:
            messages.error(request, "❌ Vui lòng chọn file hợp lệ trước khi nộp.")

    # --- 3️⃣ Render ra giao diện ---
    return render(request, "cvs/upload_cv.html", {
        "form": form,
        "analyzed_data": analyzed_data,
        "score": cv_score,
        "match_results": match_results,
        "current_cv": current_cv,
    })

def job_list(request):
    # --- 1️⃣ Nếu chưa có job, tự fetch ---
    if Job.objects.count() == 0:
        fetch_and_save_jobs()

    # --- 2️⃣ Phân trang danh sách job ---
    job_queryset = Job.objects.all().order_by('-created_at')
    paginator = Paginator(job_queryset, 10)  # mỗi trang 10 jobs
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    return render(request, "cvs/job_list.html", {
        "jobs": jobs
    })

def candidate_list(request):
    # --- 1️⃣ Lấy top ứng viên tiềm năng ---
    # Lấy nhiều hơn 5 nếu là trang danh sách riêng, ví dụ 20
    cvs = CV.objects.all().order_by('-potential_score', '-created_at')[:20]

    return render(request, "cvs/candidate_list.html", {
        "cvs": cvs
    })
