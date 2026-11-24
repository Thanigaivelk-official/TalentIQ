import uuid
from django.db import models
from django.conf import settings
from apps.organizations.models import Organization

class Job(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full-time'
        PART_TIME = 'PART_TIME', 'Part-time'
        CONTRACT = 'CONTRACT', 'Contract'
        REMOTE = 'REMOTE', 'Remote'
        INTERNSHIP = 'INTERNSHIP', 'Internship'

    class ExperienceLevel(models.TextChoices):
        ENTRY = 'ENTRY', 'Entry Level (0-2 yrs)'
        MID = 'MID', 'Mid Level (3-5 yrs)'
        SENIOR = 'SENIOR', 'Senior Level (5-8 yrs)'
        LEAD = 'LEAD', 'Lead / Principal (8+ yrs)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='jobs')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='posted_jobs')
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=150)
    location = models.CharField(max_length=150, default='Remote')
    employment_type = models.CharField(max_length=50, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    experience_level = models.CharField(max_length=50, choices=ExperienceLevel.choices, default=ExperienceLevel.MID)
    min_years_experience = models.FloatField(default=2.0)
    
    description = models.TextField()
    responsibilities = models.TextField(blank=True, default='')
    education_requirements = models.CharField(max_length=255, default="Bachelor's Degree in Computer Science or related field")
    
    # AI Extracted metadata fields
    extracted_keywords = models.JSONField(default=list, blank=True)
    ai_summary = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} - {self.department} ({self.organization.name})"


class JobSkill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='required_skills')
    name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0) # Weight multiplier for scoring
    category = models.CharField(max_length=100, default='Technical')

    class Meta:
        unique_together = ('job', 'name')
        indexes = [
            models.Index(fields=['job', 'name']),
        ]

    def __str__(self):
        req = "Required" if self.is_required else "Optional"
        return f"{self.name} ({req}) for {self.job.title}"
