import re
from typing import List, Dict, Any

# Standard technical skill taxonomy for reliable offline extraction
SKILL_TAXONOMY = {
    # Backend & Languages
    "Python", "Django", "FastAPI", "Flask", "Java", "Spring Boot", "C++", "C#", ".NET",
    "Go", "Golang", "Rust", "Node.js", "Express.js", "PHP", "Laravel", "Ruby", "Ruby on Rails",
    
    # Frontend
    "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "HTML5", "CSS3", "Tailwind CSS",
    "Bootstrap", "Next.js", "Redux", "GraphQL", "Three.js", "WebGL", "GSAP",
    
    # Data Science, AI & ML
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision",
    "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "spaCy", "Pandas", "NumPy", "OpenCV",
    "LLM", "Prompt Engineering", "LangChain", "Hugging Face", "BERT", "Transformers",
    
    # Database & Storage
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
    "Oracle", "SQL Server", "DynamoDB", "Firebase",
    
    # Cloud & DevOps
    "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "CI/CD", "GitHub Actions", "GitLab CI", "Terraform", "Ansible", "Linux", "Nginx", "Apache",
    
    # Engineering & Architecture
    "REST API", "Microservices", "System Design", "Agile", "Scrum", "Git", "GitHub", "Unit Testing",
    "TDD", "Integration Testing", "Celery", "Kafka", "RabbitMQ"
}

class NLPEngine:
    """
    NLP service extracting structured attributes (emails, phones, skills, experience)
    from candidate resumes and job descriptions.
    """
    
    @staticmethod
    def extract_email(text: str) -> str:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text: str) -> str:
        # Matches formats like +1-555-555-5555, (555) 555-5555, +91 9876543210, etc.
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return match.group(0).strip() if match else ""

    @staticmethod
    def extract_name(text: str) -> str:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:5]:
            # Simple heuristic: clean name line without email, phone, or symbols
            if len(line.split()) in [2, 3, 4] and not re.search(r'[@\d\(\)\+:,]', line):
                if not any(keyword in line.lower() for keyword in ['resume', 'curriculum', 'vitae', 'page', 'profile']):
                    return line
        return ""

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        found_skills = set()
        text_lower = text.lower()
        
        for skill in SKILL_TAXONOMY:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
                
        return sorted(list(found_skills))

    @staticmethod
    def extract_experience_years(text: str) -> float:
        # Match patterns like "5 years", "3+ years of experience", "6.5 yrs"
        matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?', text, re.IGNORECASE)
        if matches:
            years = [float(m) for m in matches if float(m) < 45]
            if years:
                return max(years)
        return 1.0

    @staticmethod
    def extract_education(text: str) -> List[Dict[str, str]]:
        degrees = ["Ph.D", "PhD", "Master", "M.S.", "MS", "M.Tech", "Bachelor", "B.S.", "BS", "B.Tech", "B.E."]
        results = []
        text_lower = text.lower()
        for deg in degrees:
            if re.search(r'\b' + re.escape(deg.lower()) + r'\b', text_lower):
                results.append({"degree": deg, "field": "Computer Science / Related"})
        return results
