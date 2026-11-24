import uuid
from django.db import models
from apps.jobs.models import Job
from apps.accounts.models import CandidateProfile
from apps.matching.models import ResumeAnalysis

class InterviewQuestion(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'

    class QuestionType(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Technical Concept'
        CODING = 'CODING', 'Practical Coding / Architecture'
        SCENARIO = 'SCENARIO', 'Scenario & Problem Solving'
        HR = 'HR', 'Behavioral & HR'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='interview_questions')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='interview_questions', null=True, blank=True)
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='interview_questions', null=True, blank=True)
    
    question = models.TextField()
    category = models.CharField(max_length=50, choices=QuestionType.choices, default=QuestionType.TECHNICAL)
    difficulty = models.CharField(max_length=50, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE)
    targeted_skill_or_gap = models.CharField(max_length=150, blank=True, default='')
    expected_answer_guide = models.TextField(blank=True, default='')
    
    is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'difficulty']

    def __str__(self):
        return f"[{self.category}] {self.question[:60]}..."
