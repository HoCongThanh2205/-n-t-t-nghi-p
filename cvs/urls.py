# cvs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_cv, name='upload_cv'),
    path('apply/<int:cv_id>/<int:job_id>/', views.apply_job, name='apply_job'),
]
