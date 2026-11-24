import os
import re
import fitz  # PyMuPDF
import docx

class DocumentProcessor:
    """
    Service responsible for secure text extraction from PDF and DOCX files.
    """
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return DocumentProcessor._extract_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentProcessor._extract_from_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported document format: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text() + "\n"
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
        return text

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for p in doc.paragraphs:
                if p.text:
                    text += p.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    text += " | ".join([c.text.strip() for c in row.cells if c.text.strip()]) + "\n"
        except Exception as e:
            raise RuntimeError(f"Error extracting text from DOCX: {str(e)}")
        return text

    @staticmethod
    def clean_text(raw_text: str) -> str:
        if not raw_text:
            return ""
        # Remove non-printable characters
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', raw_text)
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
