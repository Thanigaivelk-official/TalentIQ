import hashlib
import os
from apps.resumes.models import Resume, ExtractedResumeData
from apps.accounts.models import CandidateProfile
from apps.candidates.models import CandidateSkill
from apps.audit.models import AuditLog
from services.document_processor import DocumentProcessor
from services.nlp_engine import NLPEngine
from services.llm_provider import get_llm_provider

class ResumeParsingPipeline:
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def process_resume(cls, resume: Resume) -> ExtractedResumeData:
        try:
            resume.status = Resume.ProcessingStatus.PROCESSING
            resume.save(update_fields=['status'])

            file_path = resume.file.path
            raw_text = DocumentProcessor.extract_text(file_path)
            cleaned_text = DocumentProcessor.clean_text(raw_text)

            resume.raw_text = raw_text
            resume.cleaned_text = cleaned_text

            # Execute LLM or deterministic fallback
            provider = get_llm_provider()
            parsed_data = provider.extract_resume_data(cleaned_text)

            # Fallback augmentations if provider output is partial
            full_name = parsed_data.get('full_name') or NLPEngine.extract_name(raw_text) or "Candidate " + str(resume.id)[:6]
            email = parsed_data.get('email') or NLPEngine.extract_email(raw_text) or f"candidate_{resume.id[:8]}@talentiq.local"
            phone = parsed_data.get('phone') or NLPEngine.extract_phone(raw_text) or ""
            skills = parsed_data.get('skills') or NLPEngine.extract_skills(raw_text)
            years_exp = float(parsed_data.get('years_of_experience') or NLPEngine.extract_experience_years(raw_text))

            extracted, _ = ExtractedResumeData.objects.update_or_create(
                resume=resume,
                defaults={
                    'full_name': full_name,
                    'email': email,
                    'phone': phone,
                    'skills': skills,
                    'total_experience_years': years_exp,
                    'education': parsed_data.get('education', []),
                    'work_experience': parsed_data.get('work_experience', []),
                    'projects': parsed_data.get('projects', []),
                    'certifications': parsed_data.get('certifications', []),
                    'professional_summary': parsed_data.get('summary', ''),
                    'confidence_score': 0.92 if skills else 0.70
                }
            )

            # Sync CandidateProfile
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "Applicant"

            candidate, _ = CandidateProfile.objects.update_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'years_of_experience': years_exp,
                }
            )

            # Store individual CandidateSkill records
            CandidateSkill.objects.filter(resume=resume).delete()
            for s in skills:
                CandidateSkill.objects.create(
                    candidate=candidate,
                    resume=resume,
                    name=s,
                    category='Technical'
                )

            resume.status = Resume.ProcessingStatus.COMPLETED
            resume.save(update_fields=['status', 'raw_text', 'cleaned_text'])

            AuditLog.objects.create(
                organization=resume.organization,
                actor=resume.uploaded_by,
                action=AuditLog.Action.ANALYZE,
                resource_type='Resume',
                resource_id=str(resume.id),
                details={'status': 'completed', 'skills_count': len(skills), 'candidate': full_name}
            )

            return extracted

        except Exception as e:
            resume.status = Resume.ProcessingStatus.FAILED
            resume.error_message = str(e)
            resume.save(update_fields=['status', 'error_message'])
            raise e
