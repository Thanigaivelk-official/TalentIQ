from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.http import FileResponse, Http404
from apps.organizations.models import Organization
from apps.accounts.models import User, RecruiterProfile, CandidateProfile
from apps.jobs.models import Job, JobSkill
from apps.resumes.models import Resume, ExtractedResumeData
from apps.matching.models import ResumeAnalysis, MatchResult
from apps.interviews.models import InterviewQuestion
from apps.audit.models import AuditLog
from services.resume_parser import ResumeParsingPipeline
from services.matching_engine import MatchingEngine
from services.llm_provider import get_llm_provider
import os

def landing_view(request):
    return render(request, 'public/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            AuditLog.objects.create(
                organization=user.organization,
                actor=user,
                action=AuditLog.Action.LOGIN,
                resource_type='User',
                resource_id=str(user.id)
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please verify your email and password.')
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        org_name = request.POST.get('organization_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not (email and password and org_name):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html')

        slug = org_name.lower().replace(' ', '-').replace('.', '')
        org, _ = Organization.objects.get_or_create(name=org_name, defaults={'slug': slug})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            organization=org,
            role=User.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, f'Welcome to TalentIQ, {first_name}!')
        return redirect('dashboard')
    return render(request, 'accounts/register.html')

def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            organization=request.user.organization,
            actor=request.user,
            action=AuditLog.Action.LOGOUT,
            resource_type='User',
            resource_id=str(request.user.id)
        )
        logout(request)
    return redirect('landing')

@login_required
def dashboard_view(request):
    org = request.user.organization
    resumes = Resume.objects.filter(organization=org) if org else Resume.objects.all()
    jobs = Job.objects.filter(organization=org) if org else Job.objects.all()
    candidates = CandidateProfile.objects.all()

    avg_score = ResumeAnalysis.objects.aggregate(Avg('overall_score'))['overall_score__avg'] or 0.0

    context = {
        'total_resumes': resumes.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_candidates': candidates.count(),
        'avg_match_score': round(avg_score, 1),
        'jobs': jobs.filter(is_active=True)[:5],
        'high_count': ResumeAnalysis.objects.filter(overall_score__gte=80).count(),
        'mid_count': ResumeAnalysis.objects.filter(overall_score__gte=60, overall_score__lt=80).count(),
        'low_count': ResumeAnalysis.objects.filter(overall_score__lt=60).count(),
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def job_list_view(request):
    org = request.user.organization
    jobs = Job.objects.filter(organization=org) if org else Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def job_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        department = request.POST.get('department', '').strip()
        location = request.POST.get('location', 'Remote')
        employment_type = request.POST.get('employment_type', 'FULL_TIME')
        min_years = float(request.POST.get('min_years_experience', 2.0))
        description = request.POST.get('description', '').strip()
        required_skills = request.POST.get('required_skills', '').split(',')
        optional_skills = request.POST.get('optional_skills', '').split(',')

        org = request.user.organization
        if not org:
            org = Organization.objects.first() or Organization.objects.create(name="Default Org", slug="default-org")

        job = Job.objects.create(
            organization=org,
            created_by=request.user,
            title=title,
            department=department,
            location=location,
            employment_type=employment_type,
            min_years_experience=min_years,
            description=description
        )

        for s in required_skills:
            s_clean = s.strip()
            if s_clean:
                JobSkill.objects.create(job=job, name=s_clean, is_required=True)

        for s in optional_skills:
            s_clean = s.strip()
            if s_clean:
                JobSkill.objects.create(job=job, name=s_clean, is_required=False)

        AuditLog.objects.create(
            organization=org,
            actor=request.user,
            action=AuditLog.Action.CREATE,
            resource_type='Job',
            resource_id=str(job.id),
            details={'title': title}
        )

        messages.success(request, f"Job '{title}' successfully created.")
        return redirect('job_list')

    return render(request, 'jobs/job_form.html')

@login_required
def resume_upload_view(request):
    org = request.user.organization
    if not org:
        org = Organization.objects.first() or Organization.objects.create(name="Default Org", slug="default-org")

    if request.method == 'POST' and request.FILES.getlist('resume_files'):
        files = request.FILES.getlist('resume_files')
        job_id = request.POST.get('job_id')
        job = Job.objects.filter(id=job_id).first() if job_id else None

        processed_count = 0
        for f in files:
            # Create Resume record
            resume = Resume.objects.create(
                organization=org,
                uploaded_by=request.user,
                file=f,
                original_filename=f.name,
                file_size=f.size,
                file_hash=str(f.size) + "_" + f.name
            )

            # Process through pipeline
            try:
                extracted = ResumeParsingPipeline.process_resume(resume)
                processed_count += 1

                # If job was selected, run matching engine
                if job:
                    job_data = {
                        'title': job.title,
                        'description': job.description,
                        'min_years_experience': job.min_years_experience,
                        'required_skills': [s.name for s in job.required_skills.filter(is_required=True)],
                        'optional_skills': [s.name for s in job.required_skills.filter(is_required=False)]
                    }
                    candidate_data = {
                        'skills': extracted.skills,
                        'years_of_experience': extracted.total_experience_years,
                        'education': extracted.education,
                        'projects': extracted.projects,
                        'summary': extracted.professional_summary
                    }
                    eval_result = MatchingEngine.evaluate(job_data, candidate_data)

                    candidate = CandidateProfile.objects.filter(email=extracted.email).first()
                    analysis, _ = ResumeAnalysis.objects.update_or_create(
                        resume=resume,
                        job=job,
                        defaults={
                            'candidate': candidate,
                            'overall_score': eval_result['overall_score'],
                            'technical_skill_score': eval_result['technical_skill_score'],
                            'experience_score': eval_result['experience_score'],
                            'project_score': eval_result['project_score'],
                            'education_score': eval_result['education_score'],
                            'matched_skills': eval_result['matched_skills'],
                            'missing_skills': eval_result['missing_skills'],
                            'preferred_matches': eval_result['preferred_matches'],
                            'explanation': eval_result['explanation'],
                            'strengths': eval_result['strengths'],
                            'concerns': eval_result['concerns'],
                        }
                    )
            except Exception as e:
                messages.warning(request, f"Error processing {f.name}: {str(e)}")

        messages.success(request, f"Successfully uploaded and analyzed {processed_count} resume(s).")
        if job:
            return redirect('candidate_ranking', job_id=job.id)
        return redirect('dashboard')

    jobs = Job.objects.filter(organization=org, is_active=True) if org else Job.objects.filter(is_active=True)
    return render(request, 'resumes/upload.html', {'jobs': jobs})

@login_required
def candidate_ranking_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    analyses = ResumeAnalysis.objects.filter(job=job).select_related('candidate', 'resume').order_by('-overall_score')
    return render(request, 'candidates/ranking.html', {'job': job, 'analyses': analyses})

@login_required
def candidate_detail_view(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis.objects.select_related('candidate', 'job', 'resume'), id=analysis_id)
    return render(request, 'candidates/detail.html', {'analysis': analysis})

@login_required
def generate_interview_questions_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    questions = InterviewQuestion.objects.filter(job=job)

    if not questions.exists():
        # Generate with provider
        provider = get_llm_provider()
        req_skills = [s.name for s in job.required_skills.filter(is_required=True)]
        analyses = ResumeAnalysis.objects.filter(job=job)
        cand_skills = []
        missing_skills = []
        if analyses.exists():
            cand_skills = analyses.first().matched_skills
            missing_skills = analyses.first().missing_skills

        generated = provider.generate_interview_questions(job.title, req_skills, cand_skills, missing_skills)
        for q in generated:
            InterviewQuestion.objects.create(
                job=job,
                question=q.get('question'),
                category=q.get('category', 'TECHNICAL'),
                difficulty=q.get('difficulty', 'INTERMEDIATE'),
                targeted_skill_or_gap=q.get('targeted_skill_or_gap', ''),
                expected_answer_guide=q.get('expected_answer_guide', '')
            )
        questions = InterviewQuestion.objects.filter(job=job)

    return render(request, 'interviews/questions.html', {'job': job, 'questions': questions})

@login_required
def org_recruiters_view(request):
    user = request.user
    if user.role not in [User.Role.ORG_ADMIN, User.Role.SUPER_ADMIN] and not user.is_staff:
        messages.error(request, "Access restricted to Enterprise Organization Administrators.")
        return redirect('dashboard')

    org = user.organization
    if not org:
        messages.error(request, "Your account is not associated with an enterprise organization.")
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            title = request.POST.get('title', '').strip()
            department = request.POST.get('department', '').strip()
            role = request.POST.get('role', User.Role.RECRUITER)

            if User.objects.filter(email=email).exists():
                messages.error(request, f"An account with email '{email}' already exists.")
            else:
                new_user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    organization=org,
                    role=role
                )
                RecruiterProfile.objects.create(
                    user=new_user,
                    title=title or "Technical Recruiter",
                    department=department or "Human Resources"
                )
                AuditLog.objects.create(
                    organization=org,
                    actor=user,
                    action=AuditLog.Action.CREATE,
                    resource_type='Recruiter',
                    resource_id=str(new_user.id),
                    details={'added_recruiter': email, 'role': role}
                )
                messages.success(request, f"Recruiter '{first_name} {last_name}' successfully added to {org.name}.")

        elif action == 'edit':
            user_id = request.POST.get('user_id')
            recruiter = get_object_or_404(User, id=user_id, organization=org)

            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            new_email = request.POST.get('email', '').strip().lower()
            title = request.POST.get('title', '').strip()
            department = request.POST.get('department', '').strip()
            role = request.POST.get('role', User.Role.RECRUITER)
            new_password = request.POST.get('new_password', '').strip()

            # Admin-only email update with uniqueness check
            if new_email and new_email != recruiter.email:
                if User.objects.filter(email=new_email).exclude(id=recruiter.id).exists():
                    messages.error(request, f"Cannot update email: '{new_email}' is already in use by another account.")
                    return redirect('org_recruiters')
                old_email = recruiter.email
                recruiter.email = new_email
                recruiter.username = new_email
                AuditLog.objects.create(
                    organization=org,
                    actor=user,
                    action=AuditLog.Action.UPDATE,
                    resource_type='UserEmail',
                    resource_id=str(recruiter.id),
                    details={'old_email': old_email, 'new_email': new_email}
                )

            recruiter.first_name = first_name
            recruiter.last_name = last_name
            recruiter.role = role
            if new_password:
                recruiter.set_password(new_password)
            recruiter.save()

            profile, _ = RecruiterProfile.objects.get_or_create(user=recruiter)
            profile.title = title
            profile.department = department
            profile.save()

            AuditLog.objects.create(
                organization=org,
                actor=user,
                action=AuditLog.Action.UPDATE,
                resource_type='Recruiter',
                resource_id=str(recruiter.id),
                details={'updated_recruiter': recruiter.email}
            )
            messages.success(request, f"Recruiter '{recruiter.get_full_name()}' ({recruiter.email}) updated successfully.")

        return redirect('org_recruiters')

    if user.role == User.Role.SUPER_ADMIN or user.is_superuser:
        # Super Administrator sees all recruiters across the entire platform
        team_members = User.objects.all().select_related('organization', 'recruiter_profile').order_by('-date_joined')
    else:
        # Organization Administrator sees all recruiters in their organization
        team_members = User.objects.filter(organization=org).select_related('organization', 'recruiter_profile').order_by('-date_joined')

    return render(request, 'organizations/team.html', {'org': org, 'team_members': team_members})

@login_required
def recruiter_profile_view(request):
    user = request.user
    profile, _ = RecruiterProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        title = request.POST.get('title', '').strip()
        department = request.POST.get('department', '').strip()
        bio = request.POST.get('bio', '').strip()

        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=['first_name', 'last_name'])

        profile.title = title
        profile.department = department
        profile.bio = bio

        # Handle profile picture upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        AuditLog.objects.create(
            organization=user.organization,
            actor=user,
            action=AuditLog.Action.UPDATE,
            resource_type='RecruiterProfile',
            resource_id=str(profile.id),
            details={'updated_by': user.email}
        )

        messages.success(request, 'Your recruiter profile has been updated successfully.')
        return redirect('recruiter_profile')

    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def resume_download_view(request, resume_id):
    org = request.user.organization
    if org:
        resume = get_object_or_404(Resume, id=resume_id, organization=org)
    else:
        resume = get_object_or_404(Resume, id=resume_id)

    if not resume.file:
        raise Http404("Resume file not found.")

    try:
        response = FileResponse(resume.file.open('rb'), as_attachment=True, filename=resume.original_filename)
        AuditLog.objects.create(
            organization=resume.organization,
            actor=request.user,
            action=AuditLog.Action.EXPORT,
            resource_type='Resume',
            resource_id=str(resume.id),
            details={'downloaded_filename': resume.original_filename}
        )
        return response
    except Exception:
        raise Http404("Resume file could not be read.")

@login_required
def analytics_view(request):
    return render(request, 'analytics/index.html')
