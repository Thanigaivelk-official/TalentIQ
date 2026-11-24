import pytest
from django.test import TestCase, Client
from django.urls import reverse
from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.jobs.models import Job, JobSkill
from services.nlp_engine import NLPEngine
from services.matching_engine import MatchingEngine
from services.llm_provider import MockLLMProvider

class TestNLPAndMatching(TestCase):
    def test_nlp_extraction(self):
        sample_resume = """
        John Doe
        john.doe@example.com
        (555) 123-4567
        Senior Python Engineer with 6 years of experience in Django, Docker, PostgreSQL, and AWS.
        Master of Science in Computer Science.
        """
        email = NLPEngine.extract_email(sample_resume)
        self.assertEqual(email, "john.doe@example.com")

        phone = NLPEngine.extract_phone(sample_resume)
        self.assertIn("555", phone)

        skills = NLPEngine.extract_skills(sample_resume)
        self.assertIn("Python", skills)
        self.assertIn("Django", skills)
        self.assertIn("Docker", skills)
        self.assertIn("PostgreSQL", skills)

        exp = NLPEngine.extract_experience_years(sample_resume)
        self.assertEqual(exp, 6.0)

    def test_matching_engine_computation(self):
        job_data = {
            'title': 'Senior Python Developer',
            'description': 'Building scalable backend APIs using Django and Docker.',
            'min_years_experience': 4.0,
            'required_skills': ['Python', 'Django', 'PostgreSQL'],
            'optional_skills': ['Docker', 'AWS']
        }
        candidate_data = {
            'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
            'years_of_experience': 5.0,
            'projects': [{'title': 'Data Pipeline', 'description': 'Engineered Python Django architecture'}],
            'education': [{'degree': 'B.S.', 'field': 'Computer Science'}],
            'summary': 'Senior Python developer with experience in Django, Docker and databases.'
        }
        result = MatchingEngine.evaluate(job_data, candidate_data)
        
        self.assertGreaterEqual(result['overall_score'], 80.0)
        self.assertIn('Python', result['matched_skills'])
        self.assertIn('Django', result['matched_skills'])
        self.assertEqual(len(result['missing_skills']), 0)
        self.assertIn('confidence_level', result)

    def test_llm_provider_fallback(self):
        mock_provider = MockLLMProvider()
        questions = mock_provider.generate_interview_questions(
            job_title="Backend Engineer",
            required_skills=["Python", "PostgreSQL"],
            candidate_skills=["Python"],
            missing_skills=["PostgreSQL"]
        )
        self.assertTrue(len(questions) >= 3)
        self.assertTrue(any(q['targeted_skill_or_gap'] == 'PostgreSQL' for q in questions))


class TestWebEndpoints(TestCase):
    def setUp(self):
        self.client = Client()
        self.org = Organization.objects.create(name="Tech Innovations", slug="tech-innovations")
        self.user = User.objects.create_user(
            email="recruiter@tech.com",
            password="securePassword123!",
            organization=self.org,
            role=User.Role.RECRUITER
        )

    def test_landing_page(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TalentIQ")
        self.assertContains(response, "hero-3d-canvas")

    def test_login_and_dashboard_access(self):
        login_success = self.client.login(username="recruiter@tech.com", password="securePassword123!")
        self.assertTrue(login_success)

        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, "Recruitment Intelligence Hub")

    def test_job_creation(self):
        self.client.login(username="recruiter@tech.com", password="securePassword123!")
        response = self.client.post(reverse('job_create'), {
            'title': 'AI Software Engineer',
            'department': 'Artificial Intelligence',
            'location': 'Remote',
            'employment_type': 'FULL_TIME',
            'min_years_experience': '3.0',
            'required_skills': 'Python, PyTorch, Scikit-Learn',
            'optional_skills': 'Docker, FastAPI',
            'description': 'Developing predictive talent intelligence matching models.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Job.objects.filter(title='AI Software Engineer').exists())
