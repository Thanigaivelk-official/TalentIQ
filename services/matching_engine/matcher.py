import math
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MatchingEngine:
    """
    Transparent, auditable candidate-to-job matching engine.
    
    Default configurable weights:
    - Technical skills: 45%
    - Relevant experience: 25%
    - Project relevance: 15%
    - Education: 10%
    - Job-specific keywords / cosine similarity: 5%
    """
    
    DEFAULT_WEIGHTS = {
        'technical_skills': 0.45,
        'experience': 0.25,
        'projects': 0.15,
        'education': 0.10,
        'semantic_similarity': 0.05
    }

    @classmethod
    def evaluate(cls, job_data: Dict[str, Any], candidate_data: Dict[str, Any], weights: Dict[str, float] = None) -> Dict[str, Any]:
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS

        required_skills = [s.strip().lower() for s in job_data.get('required_skills', [])]
        optional_skills = [s.strip().lower() for s in job_data.get('optional_skills', [])]
        candidate_skills = [s.strip().lower() for s in candidate_data.get('skills', [])]

        # 1. Technical Skills Score
        matched_required = [s for s in required_skills if s in candidate_skills]
        missing_required = [s for s in required_skills if s not in candidate_skills]
        matched_optional = [s for s in optional_skills if s in candidate_skills]

        if required_skills:
            req_ratio = len(matched_required) / len(required_skills)
        else:
            req_ratio = 1.0

        opt_bonus = (len(matched_optional) / max(len(optional_skills), 1)) * 0.1
        skill_score = min(1.0, req_ratio + opt_bonus) * 100.0

        # 2. Experience Relevance Score
        min_years = float(job_data.get('min_years_experience', 2.0))
        cand_years = float(candidate_data.get('years_of_experience', 0.0))
        if min_years <= 0:
            exp_score = 100.0
        elif cand_years >= min_years:
            exp_score = 100.0
        else:
            exp_score = max(0.0, (cand_years / min_years) * 100.0)

        # 3. Project Relevance Score
        projects = candidate_data.get('projects', [])
        if projects:
            proj_text = " ".join([p.get('title', '') + " " + p.get('description', '') for p in projects]).lower()
            proj_matches = sum(1 for s in (required_skills + optional_skills) if s in proj_text)
            proj_score = min(100.0, (proj_matches / max(len(required_skills), 1)) * 100.0 + 40.0)
        else:
            proj_score = 50.0  # Fair neutral baseline when projects section isn't explicitly itemized

        # 4. Education Score
        education = candidate_data.get('education', [])
        edu_score = 75.0
        if education:
            edu_score = 90.0

        # 5. Semantic / TF-IDF Similarity
        job_corpus = (job_data.get('title', '') + " " + job_data.get('description', '') + " " + " ".join(required_skills)).strip()
        cand_corpus = (candidate_data.get('summary', '') + " " + " ".join(candidate_skills)).strip()
        
        sim_score = 50.0
        try:
            if job_corpus and cand_corpus:
                tfidf = TfidfVectorizer(stop_words='english')
                tfidf_matrix = tfidf.fit_transform([job_corpus, cand_corpus])
                sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                sim_score = float(sim * 100.0)
        except Exception:
            sim_score = 50.0

        # Calculate weighted overall score
        overall_score = (
            (skill_score * weights['technical_skills']) +
            (exp_score * weights['experience']) +
            (proj_score * weights['projects']) +
            (edu_score * weights['education']) +
            (sim_score * weights['semantic_similarity'])
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Strengths & Gaps explanation
        strengths = []
        concerns = []

        if matched_required:
            strengths.append(f"Demonstrated core required skills: {', '.join([s.title() for s in matched_required[:4]])}")
        if cand_years >= min_years:
            strengths.append(f"Meets or exceeds minimum required experience ({cand_years:.1f} yrs vs {min_years:.1f} yrs target)")
        if matched_optional:
            strengths.append(f"Possesses preferred skillsets: {', '.join([s.title() for s in matched_optional[:3]])}")

        if missing_required:
            concerns.append(f"Unverified job-specific required skills: {', '.join([s.title() for s in missing_required[:4]])}")
        if cand_years < min_years:
            concerns.append(f"Experience below requested baseline ({cand_years:.1f} yrs vs {min_years:.1f} yrs)")

        explanation = (
            f"Candidate achieved an overall matching score of {overall_score}%. "
            f"Technical proficiency assessed at {skill_score:.1f}%, experience alignment at {exp_score:.1f}%, "
            f"and project relevance at {proj_score:.1f}%. "
            f"Note: Scores represent algorithmic decision support and must be validated through human interview assessment."
        )

        return {
            "overall_score": overall_score,
            "technical_skill_score": round(skill_score, 1),
            "experience_score": round(exp_score, 1),
            "project_score": round(proj_score, 1),
            "education_score": round(edu_score, 1),
            "semantic_score": round(sim_score, 1),
            "matched_skills": [s.title() for s in matched_required],
            "missing_skills": [s.title() for s in missing_required],
            "preferred_matches": [s.title() for s in matched_optional],
            "strengths": strengths,
            "concerns": concerns,
            "explanation": explanation,
            "confidence_level": "High" if len(candidate_skills) >= 3 else "Medium"
        }
