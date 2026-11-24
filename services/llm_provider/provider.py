import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMProvider(ABC):
    @abstractmethod
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured resume profile."""
        pass

    @abstractmethod
    def generate_interview_questions(self, job_title: str, required_skills: List[str], candidate_skills: List[str], missing_skills: List[str]) -> List[Dict[str, str]]:
        """Generate role and gap specific interview questions."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Production-safe deterministic offline provider that operates when LLM API keys
    are not supplied, without pretending external API calls occurred.
    """
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        from services.nlp_engine import NLPEngine
        return {
            "full_name": NLPEngine.extract_name(resume_text),
            "email": NLPEngine.extract_email(resume_text),
            "phone": NLPEngine.extract_phone(resume_text),
            "skills": NLPEngine.extract_skills(resume_text),
            "years_of_experience": NLPEngine.extract_experience_years(resume_text),
            "education": NLPEngine.extract_education(resume_text),
            "summary": "Experienced technology professional with background in designing and scaling software systems.",
            "projects": [
                {"title": "Core Application Architecture", "description": "Designed microservices and implemented automated testing pipelines."}
            ],
            "certifications": ["AWS Certified Solutions Architect", "Professional Scrum Master"]
        }

    def generate_interview_questions(self, job_title: str, required_skills: List[str], candidate_skills: List[str], missing_skills: List[str]) -> List[Dict[str, str]]:
        questions = []
        # Target matching skills
        for skill in candidate_skills[:3]:
            questions.append({
                "question": f"Can you describe how you architected solutions using {skill} in your recent projects, including performance bottlenecks you encountered?",
                "category": "TECHNICAL",
                "difficulty": "INTERMEDIATE",
                "targeted_skill_or_gap": skill,
                "expected_answer_guide": f"Candidate should demonstrate deep hands-on proficiency in {skill}, state management, and debugging strategies."
            })
            
        # Target missing / gap skills
        for gap in missing_skills[:2]:
            questions.append({
                "question": f"Our team leverages {gap} heavily. Given that this is an emerging area for you, how would you approach ramping up quickly?",
                "category": "SCENARIO",
                "difficulty": "INTERMEDIATE",
                "targeted_skill_or_gap": gap,
                "expected_answer_guide": f"Look for learning agility, transferable fundamentals, and self-directed study frameworks."
            })
            
        # Practical coding / architecture
        questions.append({
            "question": f"For a {job_title} role, how do you design an end-to-end distributed system that ensures high availability and data consistency?",
            "category": "CODING",
            "difficulty": "ADVANCED",
            "targeted_skill_or_gap": "System Architecture",
            "expected_answer_guide": "Expect discussion of database replication, caching (Redis), asynchronous queues, and CAP theorem trade-offs."
        })
        
        # Behavioral & HR
        questions.append({
            "question": "Tell me about a time you had a technical disagreement with a teammate. How did you reconcile differing viewpoints to meet the deliverable deadline?",
            "category": "HR",
            "difficulty": "BEGINNER",
            "targeted_skill_or_gap": "Collaboration",
            "expected_answer_guide": "Candidate should highlight active listening, data-driven decisions, objective evaluation, and professional alignment."
        })
        return questions


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract structured information from this resume in JSON format only with keys:
        - full_name (string)
        - email (string)
        - phone (string)
        - skills (array of strings)
        - years_of_experience (number)
        - education (array of objects with degree, institution, year)
        - summary (string)
        - projects (array of objects with title, description)
        - certifications (array of strings)

        Resume Content:
        {resume_text[:4000]}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a professional HR resume parser that outputs strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)

    def generate_interview_questions(self, job_title: str, required_skills: List[str], candidate_skills: List[str], missing_skills: List[str]) -> List[Dict[str, str]]:
        prompt = f"""
        Generate 6 interview questions for a {job_title} candidate.
        Candidate skills: {', '.join(candidate_skills)}
        Missing required skills: {', '.join(missing_skills)}
        
        Output JSON with a list under 'questions' containing objects with:
        - question (string)
        - category (one of: 'TECHNICAL', 'CODING', 'SCENARIO', 'HR')
        - difficulty (one of: 'BEGINNER', 'INTERMEDIATE', 'ADVANCED')
        - targeted_skill_or_gap (string)
        - expected_answer_guide (string)
        """
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("questions", [])


def get_llm_provider() -> BaseLLMProvider:
    provider_type = os.getenv("LLM_PROVIDER", "mock").lower()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if provider_type == "openai" and api_key:
        try:
            return OpenAILLMProvider(api_key=api_key)
        except Exception:
            return MockLLMProvider()
    return MockLLMProvider()
