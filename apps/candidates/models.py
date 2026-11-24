import uuid
from django.db import models
from apps.accounts.models import CandidateProfile
from apps.resumes.models import Resume

class CandidateSkill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='skills')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills', null=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default='Technical')
    proficiency_level = models.CharField(max_length=50, default='Intermediate')
    years_experience = models.FloatField(default=1.0)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['candidate', 'name']),
        ]

    def __str__(self):
        return f"{self.candidate} - {self.name}"
