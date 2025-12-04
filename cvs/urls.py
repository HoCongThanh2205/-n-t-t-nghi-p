# cvs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_cv, name='upload_cv'),
    path('jobs/', views.job_list, name='job_list'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('apply/<int:cv_id>/<int:job_id>/', views.apply_job, name='apply_job'),
]
