# TalentIQ – AI-Powered Resume Screening & Candidate Ranking System

> **Smarter Hiring. Better Talent. Faster Decisions.**

TalentIQ is an enterprise-grade recruitment intelligence platform designed to eliminate hiring friction, automate multi-format resume parsing (PDF, DOCX), compute transparent candidate-job matching scores, and generate interview evaluations—while actively preventing algorithmic bias.

---

## 🌟 Key Capabilities

- **3D Interactive Hero Experience**: Three.js WebGL visualization of neural knowledge representations and particle fields.
- **Multi-Format Document Parsing**: High-fidelity text and layout extraction from PDF (PyMuPDF) and Word documents (python-docx).
- **Explainable Matching Engine**: Multi-variable weighted scoring (Technical Skills 45%, Experience 25%, Projects 15%, Education 10%, Semantic Sim 5%) with transparent audit trails.
- **Provider Abstraction Layer**: Seamless plug-and-play LLM orchestration supporting OpenAI API and deterministic offline fallbacks.
- **Contextual Interview Generator**: Dynamically crafts role-specific technical questions and targeted skill-gap inquiries.
- **Enterprise Multi-Tenancy**: Organization-isolated candidate pools and audit logs.

---

## 🚀 Architecture & Tech Stack

- **Backend**: Python 3.12+, Django 6.x, Django REST Framework
- **Database**: PostgreSQL (with SQLite for local development)
- **Frontend**: Django Templates, Bootstrap 5, Custom Glassmorphic Dark Design System
- **NLP & ML**: Scikit-Learn (TF-IDF & Cosine Similarity), Custom Skill Taxonomy Engine
- **3D & Visualization**: Three.js, Lucide Icons, Chart.js
- **DevOps**: Docker, Docker Compose

---

## 🛠️ Quickstart Installation

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/Thanigaivelk-official/TalentIQ.git
cd TalentIQ
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python scripts/seed_demo.py
```

### 4. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://localhost:8000` to interact with the platform.

---

## 🔐 Demo Login Credentials

For quick evaluation and testing across roles, use the following pre-configured credentials:

| Role | Email | Password | Access & Permissions |
| :--- | :--- | :--- | :--- |
| **Organization Administrator** | `org.admin@talentiq.ai` | `TalentIQDemo2026!` | Full administrative access, manage organization team, add/edit recruiters, change recruiter emails, view audit logs. |
| **Lead Technical Recruiter** | `thanigaivelk.official@gmail.com` | `TalentIQDemo2026!` | Post jobs, upload & batch screen resumes, view candidate rankings, generate interview questions, manage profile. |
| **Demo Recruiter** | `thanigaivel.kannan@talentiq.ai` | `TalentIQDemo2026!` | Recruiter dashboard, candidate evaluation, skill gap breakdown, AI matching pipelines. |

> **Note**: You can also seed additional sample jobs and candidate profiles at any time by running:
> ```bash
> python scripts/seed_demo.py
> ```

---

## 🚀 One-Click Render Deployment

TalentIQ is fully pre-configured for automated continuous deployment on [Render](https://render.com) using Infrastructure-as-Code (`render.yaml`).

### Option 1: Render Blueprint (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Select your GitHub repository: `Thanigaivelk-official/TalentIQ`.
4. Render will automatically detect `render.yaml` and provision:
   - **PostgreSQL Database** (`talentiq-db`, Free Tier).
   - **Python Web Service** (`talentiq`, running Gunicorn + WhiteNoise on Python 3.12).
5. Click **Apply**. Render will run `./build.sh` (installs packages, collects static files, executes migrations, and seeds demo recruiter accounts) and launch the live site.

### Option 2: Manual Web Service Setup
If deploying without Blueprint:
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- **Environment Variables**:
  - `PYTHON_VERSION`: `3.12.10`
  - `DJANGO_SETTINGS_MODULE`: `config.settings.production`
  - `SECRET_KEY`: `<generate-a-secure-random-key>`
  - `DATABASE_URL`: `<your-render-postgresql-external-or-internal-url>`
  - `ALLOWED_HOSTS`: `.onrender.com,localhost,127.0.0.1`
  - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`
  - `LLM_PROVIDER`: `mock` (or provide `OPENAI_API_KEY` for live OpenAI GPT models)

---

## 🧪 Automated Testing

Run the automated test suite verifying NLP extraction, matching algorithms, and API endpoints:
```bash
python manage.py test tests.unit.test_platform
```

---

## 🐳 Docker Deployment
```bash
docker-compose up --build
```
