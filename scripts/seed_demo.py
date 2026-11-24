import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.organizations.models import Organization
from apps.accounts.models import User, RecruiterProfile, CandidateProfile
from apps.jobs.models import Job, JobSkill
from apps.resumes.models import Resume, ExtractedResumeData
from apps.matching.models import ResumeAnalysis

def seed_demo_data():
    org, _ = Organization.objects.get_or_create(
        name="Apex Global Technologies",
        defaults={'slug': 'apex-global-tech', 'domain': 'apextech.io'}
    )

    admin_email = "demo.recruiter@talentiq.ai"
    if not User.objects.filter(email=admin_email).exists():
        user = User.objects.create_user(
            email=admin_email,
            password="TalentIQDemo2026!",
            first_name="Alexandra",
            last_name="Vance",
            organization=org,
            role=User.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=user, title="Principal Technical Recruiter")
        print(f"Created demo recruiter: {admin_email} / TalentIQDemo2026!")
    else:
        user = User.objects.get(email=admin_email)

    # Demo Jobs
    job1, _ = Job.objects.get_or_create(
        organization=org,
        title="Senior AI Platform Engineer",
        defaults={
            'created_by': user,
            'department': 'Machine Learning Infrastructure',
            'location': 'Remote / San Francisco',
            'employment_type': Job.EmploymentType.FULL_TIME,
            'experience_level': Job.ExperienceLevel.SENIOR,
            'min_years_experience': 4.0,
            'description': 'Architect distributed inference pipelines and scalable microservices for production LLM systems.',
            'responsibilities': 'Scale Kubernetes deployments, fine-tune models, optimize Python services.'
        }
    )
    for skill, req in [("Python", True), ("PyTorch", True), ("Docker", True), ("FastAPI", True), ("Kubernetes", False), ("AWS", False)]:
        JobSkill.objects.get_or_create(job=job1, name=skill, defaults={'is_required': req})

    job2, _ = Job.objects.get_or_create(
        organization=org,
        title="Lead Full-Stack Python Architect",
        defaults={
            'created_by': user,
            'department': 'Core Platform',
            'location': 'Remote / New York',
            'employment_type': Job.EmploymentType.FULL_TIME,
            'experience_level': Job.ExperienceLevel.LEAD,
            'min_years_experience': 5.0,
            'description': 'Lead development of enterprise Django application platforms with high-concurrency PostgreSQL databases.',
            'responsibilities': 'Architect backend data models, optimize queries, guide frontend architectural decisions.'
        }
    )
    for skill, req in [("Python", True), ("Django", True), ("PostgreSQL", True), ("Docker", True), ("Redis", False), ("Celery", False)]:
        JobSkill.objects.get_or_create(job=job2, name=skill, defaults={'is_required': req})

    # Sample Candidates & Analyses
    candidates_info = [
        ("Sarah", "Jenkins", "sarah.jenkins@example.com", 6.5, 94.2, ["Python", "PyTorch", "Docker", "FastAPI", "Kubernetes"], job1),
        ("David", "Chen", "david.chen@example.com", 5.0, 88.5, ["Python", "Django", "PostgreSQL", "Docker", "Redis"], job2),
        ("Elena", "Rostova", "elena.rostova@example.com", 4.0, 76.0, ["Python", "Docker", "AWS"], job1),
        ("Marcus", "Brody", "marcus.brody@example.com", 7.0, 91.0, ["Python", "Django", "PostgreSQL", "Celery"], job2),
    ]

    for fname, lname, email, exp, score, skills, target_job in candidates_info:
        cand, _ = CandidateProfile.objects.get_or_create(
            email=email,
            defaults={'first_name': fname, 'last_name': lname, 'years_of_experience': exp}
        )

        dummy_resume, _ = Resume.objects.get_or_create(
            organization=org,
            original_filename=f"{fname.lower()}_{lname.lower()}_resume.pdf",
            defaults={
                'uploaded_by': user,
                'file_size': 124500,
                'file_hash': f"hash_{fname.lower()}_{lname.lower()}",
                'status': Resume.ProcessingStatus.COMPLETED
            }
        )

        ExtractedResumeData.objects.get_or_create(
            resume=dummy_resume,
            defaults={
                'full_name': f"{fname} {lname}",
                'email': email,
                'skills': skills,
                'total_experience_years': exp,
                'professional_summary': f"Experienced technical professional specializing in {', '.join(skills[:3])}."
            }
        )

        ResumeAnalysis.objects.get_or_create(
            resume=dummy_resume,
            job=target_job,
            defaults={
                'candidate': cand,
                'overall_score': score,
                'technical_skill_score': score + 2.0 if score < 95 else 98.0,
                'experience_score': 95.0,
                'project_score': 90.0,
                'education_score': 85.0,
                'matched_skills': skills[:4],
                'missing_skills': [] if score > 85 else ["FastAPI"],
                'explanation': f"Strong qualification profile with demonstrated proficiency in {', '.join(skills[:3])}.",
                'strengths': [f"Strong background in {skills[0]} and {skills[1]}", f"{exp} years of relevant industry experience"],
                'concerns': [] if score > 85 else ["Verify practical production experience with secondary requirements"]
            }
        )

    print("Demo seed completed successfully.")

if __name__ == '__main__':
    seed_demo_data()
