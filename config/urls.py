from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Jobs
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/create/', views.job_create_view, name='job_create'),
    
    # Resumes & Screening
    path('resumes/upload/', views.resume_upload_view, name='resume_upload'),
    path('resumes/<uuid:resume_id>/download/', views.resume_download_view, name='resume_download'),
    path('jobs/<uuid:job_id>/ranking/', views.candidate_ranking_view, name='candidate_ranking'),
    path('candidates/analysis/<uuid:analysis_id>/', views.candidate_detail_view, name='candidate_detail'),
    
    # Interviews & Analytics
    path('jobs/<uuid:job_id>/interviews/', views.generate_interview_questions_view, name='generate_interview_questions'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('profile/', views.recruiter_profile_view, name='recruiter_profile'),
    path('organization/team/', views.org_recruiters_view, name='org_recruiters'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
