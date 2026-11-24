import uuid
from django.db import models
from django.conf import settings
from apps.organizations.models import Organization

def resume_upload_path(instance, filename):
    return f"resumes/{instance.organization.id}/{uuid.uuid4()}_{filename}"

class Resume(models.Model):
    class ProcessingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='resumes')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_resumes')
    file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash for deduplication")
    status = models.CharField(max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING)
    error_message = models.TextField(blank=True, null=True)
    
    raw_text = models.TextField(blank=True, default='')
    cleaned_text = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'file_hash']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()})"


class ExtractedResumeData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='extracted_data')
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    location = models.CharField(max_length=150, blank=True, default='')
    professional_summary = models.TextField(blank=True, default='')
    
    total_experience_years = models.FloatField(default=0.0)
    
    # Structured JSON data
    skills = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    projects = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    confidence_score = models.FloatField(default=0.85)
    is_verified_by_recruiter = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extracted: {self.full_name or 'Unknown'} ({self.resume.original_filename})"
