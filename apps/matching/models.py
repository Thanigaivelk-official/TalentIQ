import uuid
from django.db import models
from apps.jobs.models import Job
from apps.resumes.models import Resume
from apps.accounts.models import CandidateProfile

class ResumeAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='analyses')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='analyses', null=True, blank=True)
    
    # Matching Scores (0 - 100)
    overall_score = models.FloatField(default=0.0)
    technical_skill_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    project_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    
    # Detailed findings
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    preferred_matches = models.JSONField(default=list, blank=True)
    
    # Audit & Explainability
    explanation = models.TextField(blank=True, default='')
    strengths = models.JSONField(default=list, blank=True)
    concerns = models.JSONField(default=list, blank=True)
    confidence_level = models.CharField(max_length=50, default='High')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-overall_score']
        unique_together = ('resume', 'job')
        indexes = [
            models.Index(fields=['job', 'overall_score']),
            models.Index(fields=['resume', 'job']),
        ]

    def __str__(self):
        return f"{self.resume.original_filename} vs {self.job.title} - Score: {self.overall_score}%"


class MatchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(ResumeAnalysis, on_delete=models.CASCADE, related_name='detailed_match')
    similarity_matrix = models.JSONField(default=dict, blank=True)
    scoring_weights = models.JSONField(default=dict, blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match Details for Analysis {self.analysis.id}"


class Application(models.Model):
    class Stage(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        SCREENED = 'SCREENED', 'Screened'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        INTERVIEW = 'INTERVIEW', 'Interview Stage'
        OFFER = 'OFFER', 'Offer Extended'
        HIRED = 'HIRED', 'Hired'
        ARCHIVED = 'ARCHIVED', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='applications')
    stage = models.CharField(max_length=50, choices=Stage.choices, default=Stage.APPLIED)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate} - {self.job.title} ({self.get_stage_display()})"
