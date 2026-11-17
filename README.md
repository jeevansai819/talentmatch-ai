# TalentMatch AI – Intelligent Resume Screening & Job Matching Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.15-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.28-orange.svg)](https://pymupdf.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**TalentMatch AI** is a commercial-grade, end-to-end recruitment intelligence and candidate screening platform built for HR professionals and hiring managers. It automates candidate resume intake, parses complex unstructured PDF documents with **PyMuPDF**, performs deep technical skill and experience extraction using **NLP & custom taxonomies**, and scores applicants against job descriptions with a transparent, explainable **deterministic weighted scoring engine**.

Unlike superficial prototypes, TalentMatch AI features a fully functional Python backend, responsive SaaS frontend, relational PostgreSQL/SQLite architecture, JWT security, side-by-side candidate comparison, executive PDF report generation, and real-time database analytics.

---

## 🌟 Key Features

1. **Multi-Resume Batch Upload**:
   - Drag-and-drop multiple PDF resumes simultaneously.
   - Validation against corrupted, empty, or password-protected PDFs.
   - Extraction of text, contact details, links, education, experience, and projects.

2. **NLP Skill Extraction & Canonicalization**:
   - Technical taxonomy covering 1,000+ programming languages, frameworks, cloud services, databases, and DevOps tools.
   - Word-boundary regex and phrase matching with canonical brand normalization (e.g. `k8s` -> `Kubernetes`, `postgres` -> `PostgreSQL`, `fastapi` -> `FastAPI`).

3. **Job Description & Criteria Management**:
   - Create, edit, and manage job requisitions.
   - Configurable required skills, preferred bonus skills, minimum experience duration, and minimum educational requirements.

4. **Multi-Factor Weighted Compatibility Scoring**:
   - **Required Skills Match (40%)**: Ratio of mandatory technical competencies fulfilled.
   - **Preferred Skills Match (20%)**: Bonus domain skills and secondary frameworks.
   - **Experience Duration Match (20%)**: Verified candidate tenure compared against job minimums.
   - **Education Match (10%)**: Hierarchical academic evaluation (Doctorate > Master's > Bachelor's > Associate).
   - **Textual / Semantic Similarity (10%)**: TF-IDF vectorization and Cosine Similarity between resume text and job criteria.
   - Total equals 100% (fully configurable per platform requirements).

5. **Explainable AI Matching Reports**:
   - Transparent, audit-proof reports detailing matched skills, missing skill gaps, experience differences, strengths, and narrative rationale.
   - Non-discriminatory: Strict exclusion of protected personal demographics (gender, age, race, religion, nationality).

6. **Candidate Ranking & Side-by-Side Comparison**:
   - Rank candidates from highest to lowest compatibility.
   - Tier indicators: **Excellent Match (90–100%)**, **Strong Match (75–89%)**, **Moderate Match (60–74%)**, and **Low Match (<60%)**.
   - Compare up to 5 candidates side-by-side across scores, skills, and qualifications.

7. **Executive Reporting & Export**:
   - Generate downloadable executive candidate screening reports in PDF format using **ReportLab**.
   - Export shortlisted candidate rosters with recruiter notes to standard CSV.

8. **Recruiter Lifecycle Management**:
   - Status updates (`New`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Rejected`, `Hired`) with historical audit logs.
   - Confidential recruiter assessment notes with timestamps.

9. **Live Database Analytics Dashboard**:
   - Real-time Chart.js visualizations driven by SQL aggregations: top candidate skills, experience level distribution, score histograms, and recruitment funnel stages.

---

## 🛠 Technology Stack

- **Backend**: Python 3.11+ / FastAPI / Uvicorn / Pydantic v2
- **Database & ORM**: PostgreSQL 16 (Production) / SQLite (Zero-config local), SQLAlchemy 2.0 ORM, Alembic migrations
- **AI / NLP & Extraction**: PyMuPDF 1.28 (C-MuPDF bindings), custom technical taxonomy, pure-Python Smooth-IDF TF-IDF Vectorizer & Cosine Similarity engine, spaCy
- **Security & Auth**: JWT (PyJWT), password hashing with bcrypt, role-based authorization (Recruiter / Admin)
- **Document & Export**: ReportLab 5.1 (Executive PDF reports), Python standard CSV writer
- **Frontend**: Responsive modern HTML5, CSS3 (Linear/Tailwind aesthetics), Vanilla ES6 JavaScript, Jinja2 templates, Chart.js
- **Testing**: pytest, FastAPI TestClient, in-memory SQLite isolation

---

## 📁 System Architecture

```text
talentmatch-ai/
├── app/
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings & environment variables
│   │   ├── database.py          # SQLAlchemy engine, session maker, get_db
│   │   └── security.py          # Bcrypt hashing, JWT generation & verification
│   ├── models/
│   │   ├── user.py              # Recruiter / Admin accounts
│   │   ├── candidate.py         # Candidate entity
│   │   ├── resume.py            # Stored resume metadata & extracted raw text
│   │   ├── job.py               # Job postings
│   │   ├── skill.py             # Candidate skills & Job required/preferred skills
│   │   ├── education.py         # Candidate education history
│   │   ├── experience.py        # Candidate work history
│   │   ├── matching.py          # Calculated match scores & JSON explanation reports
│   │   ├── shortlist.py         # Shortlist containers & member candidates
│   │   ├── note.py              # Recruiter confidential notes
│   │   └── audit.py             # Application status change audit history
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py              # /api/auth (register, login, me)
│   │   ├── jobs.py              # /api/jobs (CRUD job postings)
│   │   ├── resumes.py           # /api/resumes (multi-upload, download, view)
│   │   ├── candidates.py        # /api/candidates (directory, status, notes)
│   │   ├── matching.py          # /api/matching (run, results, compare, PDF)
│   │   ├── shortlists.py        # /api/shortlists (CRUD, CSV export)
│   │   ├── analytics.py         # /api/analytics/dashboard
│   │   └── web.py               # Web UI routes (Jinja2 views)
│   ├── services/
│   │   ├── pdf_extractor.py     # PyMuPDF extraction & corruption validation
│   │   ├── skill_extractor.py   # Regex & taxonomy entity extractor
│   │   ├── resume_parser.py     # End-to-end contact, degree, & experience parser
│   │   ├── matching_engine.py   # Multi-factor weighted compatibility & TF-IDF engine
│   │   ├── ranking_service.py   # Sorting, filtering, candidate comparisons
│   │   └── report_generator.py  # ReportLab PDF executive builder & CSV generator
│   ├── templates/               # 12 Jinja2 responsive HTML pages
│   └── static/                  # CSS, JS, and image assets
├── tests/                       # Automated pytest suite (18 unit & integration tests)
├── migrations/                  # Alembic database migrations
├── scripts/
│   ├── generate_sample_resumes.py # Generates valid sample PDF resumes
│   └── seed_data.py             # End-to-end database seed script
├── uploads/                     # Uploaded and sample resume storage
├── Dockerfile                   # Production container definition
├── docker-compose.yml           # Multi-container Web + PostgreSQL setup
├── requirements.txt             # Locked Python dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # System documentation
```

---

## 🚀 Quick Start Guide (Local Setup)

### 1. Prerequisites
- Python 3.11, 3.12, or compatible stable release
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/your-org/talentmatch-ai.git
cd talentmatch-ai

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
By default, `.env` points to `sqlite:///./talentmatch.db` for instant local execution without installing PostgreSQL. For production PostgreSQL, set:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/talentmatch
```

### 4. Initialize Database and Seed Sample Data
Run the automated seed script to initialize the database, create the default recruiter account, create 3 realistic job postings, generate 5 valid sample PDF resumes, run the PDF text extraction and NLP parser, and calculate real matching scores:
```bash
python scripts/seed_data.py
```

### 5. Start the Application
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Swagger UI**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)

### 6. Default Recruiter Credentials
- **Email**: `recruiter@talentmatch.ai`
- **Password**: `Recruiter123!`
*(You can also register a new account on `/register`)*

---

## 🐳 Docker Deployment

The application includes a production-grade multi-container setup using Docker Compose (FastAPI Web + PostgreSQL 16 Alpine):

```bash
# Build and run containers
docker-compose up --build -d

# Check container health status
docker-compose ps

# Seed initial database records inside the container
docker-compose exec web python scripts/seed_data.py
```

Access the application at `http://localhost:8000`.

---

## 🧪 Automated Testing

TalentMatch AI includes a comprehensive automated test suite with 18 unit and integration tests covering authentication, PDF extraction, resume parsing, matching calculations, API endpoints, shortlists, and analytics.

Execute tests using pytest:
```bash
python -m pytest tests/ -v
```

### Test Suite Summary:
```text
tests/test_analytics.py::test_analytics_dashboard_metrics PASSED         [  5%]
tests/test_auth.py::test_user_registration PASSED                        [ 11%]
tests/test_auth.py::test_duplicate_user_registration_fails PASSED        [ 16%]
tests/test_auth.py::test_user_login_success PASSED                       [ 22%]
tests/test_auth.py::test_user_login_invalid_password PASSED              [ 27%]
tests/test_auth.py::test_protected_route_without_token PASSED            [ 33%]
tests/test_auth.py::test_protected_route_with_token PASSED               [ 38%]
tests/test_jobs_api.py::test_create_and_get_job PASSED                   [ 44%]
tests/test_matching_engine.py::test_matching_engine_high_compatibility PASSED [ 50%]
tests/test_matching_engine.py::test_matching_engine_low_compatibility PASSED [ 55%]
tests/test_pdf_extractor.py::test_extract_text_valid_pdf PASSED          [ 61%]
tests/test_pdf_extractor.py::test_extract_text_missing_file PASSED       [ 66%]
tests/test_pdf_extractor.py::test_extract_text_empty_file PASSED         [ 72%]
tests/test_resume_parser.py::test_skill_extractor_taxonomy PASSED        [ 77%]
tests/test_resume_parser.py::test_resume_parser_structured_extraction PASSED [ 83%]
tests/test_resumes_api.py::test_resume_upload_and_extraction PASSED      [ 88%]
tests/test_resumes_api.py::test_resume_upload_rejects_non_pdf PASSED     [ 94%]
tests/test_shortlists_api.py::test_shortlist_lifecycle_and_csv_export PASSED [100%]

======================= 18 passed in 5.17s =======================
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new recruiter account |
| `POST` | `/api/auth/login` | Recruiter login (returns JWT Bearer token) |
| `GET` | `/api/auth/me` | Fetch authenticated recruiter profile |
| `POST` | `/api/resumes/upload` | Batch upload and parse multiple PDF resumes |
| `GET` | `/api/resumes` | List uploaded resume records |
| `GET` | `/api/resumes/{id}/download` | Download original uploaded PDF resume |
| `POST` | `/api/jobs` | Create a new job requisition with skills & criteria |
| `GET` | `/api/jobs` | List active job requisitions |
| `PUT` | `/api/jobs/{id}` | Update job posting requirements |
| `DELETE` | `/api/jobs/{id}` | Delete job requisition |
| `POST` | `/api/matching/{job_id}/run` | Execute AI matching engine for candidates |
| `GET` | `/api/matching/{job_id}/results` | Fetch ranked candidate match scores and tiers |
| `GET` | `/api/matching/results/{id}` | Fetch detailed explainable score breakdown |
| `POST` | `/api/matching/compare` | Compare up to 5 candidates side-by-side |
| `GET` | `/api/matching/{job_id}/export/pdf` | Download executive screening report (PDF) |
| `GET` | `/api/candidates` | List candidate roster with status and exp filters |
| `GET` | `/api/candidates/{id}` | Fetch complete candidate profile dossier |
| `PUT` | `/api/candidates/{id}/status` | Update candidate recruitment status with audit comment |
| `POST` | `/api/candidates/{id}/notes` | Add confidential recruiter note |
| `POST` | `/api/shortlists` | Create a candidate shortlist |
| `POST` | `/api/shortlists/{id}/candidates` | Add candidate to shortlist |
| `GET` | `/api/shortlists/{id}/export/csv` | Export shortlist candidates to CSV |
| `GET` | `/api/analytics/dashboard` | Aggregated statistical metrics and distributions |

---

## 🔒 Security & Confidentiality

- **Secure File Storage**: Uploaded files receive sanitized UUID-based identifiers preventing directory traversal (`../`) vulnerabilities.
- **Strict PDF Validation**: Validates file size (max 10MB), MIME type, and PDF internal structure via PyMuPDF.
- **Password Security**: Passwords hashed with standard bcrypt (12 salt rounds).
- **Session Security**: JWT bearer tokens with configurable expiration (default 24h).
- **Candidate Privacy**: Resumes are kept strictly confidential in local database storage. No personal data is transmitted to external generative AI services.

---

## 📄 License
This project is licensed under the MIT License.
