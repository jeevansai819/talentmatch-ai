import os
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
import app.models  # ensure models registered
from app.models.user import User
from app.models.job import Job
from app.models.skill import JobRequiredSkill, JobPreferredSkill, CandidateSkill
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.education import CandidateEducation
from app.models.experience import CandidateExperience
from app.models.matching import MatchResult
from app.models.shortlist import Shortlist, ShortlistCandidate
from app.models.audit import ApplicationStatusHistory
from app.core.security import get_password_hash
from app.services.pdf_extractor import PDFExtractor
from app.services.resume_parser import resume_parser
from app.services.matching_engine import matching_engine
from app.utils.constants import CANONICAL_SKILL_MAP
from scripts.generate_sample_resumes import generate_all_samples

def seed():
    print("Initializing TalentMatch database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Default Recruiter Account
        admin_email = "recruiter@talentmatch.ai"
        user = db.query(User).filter(User.email == admin_email).first()
        if not user:
            user = User(
                email=admin_email,
                full_name="Sarah Jenkins (Senior Talent Lead)",
                hashed_password=get_password_hash("Recruiter123!"),
                role="recruiter",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✓ Created default recruiter account: {admin_email} (Password: Recruiter123!)")
        else:
            print(f"✓ Recruiter account already exists: {admin_email}")

        # 2. Seed Job Postings
        jobs_data = [
            {
                "title": "Senior Full Stack Python Engineer",
                "department": "Engineering",
                "location": "Remote / New York",
                "employment_type": "Full-time",
                "min_experience_years": 4.0,
                "required_education_level": "Bachelor",
                "required_skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
                "preferred_skills": ["Redis", "AWS", "Kubernetes", "Next.js", "TypeScript"],
                "description": """We are seeking a Senior Full Stack Engineer to lead development of our distributed cloud platform.
You will architect microservices with Python, FastAPI, and PostgreSQL, and craft responsive frontend applications using React and TypeScript.
Ideal candidates have strong system design capabilities and experience deploying containerized services with Docker and Kubernetes on AWS."""
            },
            {
                "title": "Lead Data Scientist / NLP Specialist",
                "department": "AI & Research",
                "location": "San Francisco, CA",
                "employment_type": "Full-time",
                "min_experience_years": 3.0,
                "required_education_level": "Master",
                "required_skills": ["Python", "Machine Learning", "PyTorch", "NLP", "Pandas", "Scikit-Learn"],
                "preferred_skills": ["Transformers", "Hugging Face", "Deep Learning", "Docker", "AWS"],
                "description": """Looking for an experienced Data Scientist specializing in Natural Language Processing and Deep Learning.
You will design real-time text classification and information extraction pipelines using PyTorch, Transformers, and Scikit-Learn.
Requires advanced academic background (Master's or Ph.D.) and hands-on production modeling experience."""
            },
            {
                "title": "Senior DevOps & Cloud Infrastructure Architect",
                "department": "Infrastructure",
                "location": "Seattle, WA / Remote",
                "employment_type": "Full-time",
                "min_experience_years": 5.0,
                "required_education_level": "Bachelor",
                "required_skills": ["Kubernetes", "Docker", "Terraform", "AWS", "Linux", "CI/CD"],
                "preferred_skills": ["Prometheus", "Grafana", "Ansible", "Python", "Argo CD"],
                "description": """Lead our Cloud Infrastructure and DevOps engineering efforts.
You will manage multi-region Kubernetes clusters on AWS EKS, automate zero-downtime CI/CD deployment pipelines,
and maintain immutable infrastructure code using Terraform and Ansible."""
            }
        ]

        created_jobs = []
        for jd in jobs_data:
            existing_job = db.query(Job).filter(Job.title == jd["title"]).first()
            if not existing_job:
                new_job = Job(
                    title=jd["title"],
                    department=jd["department"],
                    location=jd["location"],
                    employment_type=jd["employment_type"],
                    min_experience_years=jd["min_experience_years"],
                    required_education_level=jd["required_education_level"],
                    description=jd["description"],
                    is_active=True,
                    created_by_id=user.id
                )
                db.add(new_job)
                db.flush()

                for s_name in jd["required_skills"]:
                    cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
                    db.add(JobRequiredSkill(job_id=new_job.id, skill_name=s_name, category=cat))

                for s_name in jd["preferred_skills"]:
                    cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
                    db.add(JobPreferredSkill(job_id=new_job.id, skill_name=s_name, category=cat))

                db.commit()
                db.refresh(new_job)
                created_jobs.append(new_job)
                print(f"✓ Created job posting: {new_job.title}")
            else:
                created_jobs.append(existing_job)

        # 3. Generate and Process Sample PDF Resumes
        print("\nGenerating sample resumes and running PDF extraction pipeline...")
        pdf_paths = generate_all_samples("./uploads")

        processed_candidates = []
        for pdf_path in pdf_paths:
            orig_filename = os.path.basename(pdf_path)
            raw_text, page_count = PDFExtractor.extract_text(pdf_path)
            parsed = resume_parser.parse(raw_text)

            # Check duplicate by email
            candidate = db.query(Candidate).filter(Candidate.email == parsed["email"].lower()).first()
            if not candidate:
                candidate = Candidate(
                    name=parsed["name"],
                    email=parsed["email"].lower(),
                    phone=parsed.get("phone"),
                    location=parsed.get("location"),
                    total_experience_years=parsed.get("total_experience_years", 0.0),
                    highest_education_level=parsed.get("highest_education_level", "Bachelor's Degree"),
                    current_status="New",
                    linkedin_url=parsed.get("linkedin_url"),
                    github_url=parsed.get("github_url"),
                    summary=parsed.get("summary")
                )
                db.add(candidate)
                db.flush()

                # Audit status
                db.add(ApplicationStatusHistory(
                    candidate_id=candidate.id,
                    old_status=None,
                    new_status="New",
                    changed_by_id=user.id,
                    comment="Initial profile parsed from PDF resume."
                ))

                # Resume file entry
                resume_rec = Resume(
                    candidate_id=candidate.id,
                    filename=orig_filename,
                    original_filename=orig_filename,
                    file_size=os.path.getsize(pdf_path),
                    mime_type="application/pdf",
                    file_path=pdf_path,
                    raw_text=raw_text,
                    parsed_successfully=True
                )
                db.add(resume_rec)

                # Candidate skills
                for s in parsed.get("skills", []):
                    db.add(CandidateSkill(
                        candidate_id=candidate.id,
                        skill_name=s["skill_name"],
                        category=s["category"],
                        confidence_score=s.get("confidence_score", 1.0)
                    ))

                # Education
                for edu in parsed.get("education", []):
                    db.add(CandidateEducation(
                        candidate_id=candidate.id,
                        degree=edu["degree"],
                        field_of_study=edu.get("field_of_study"),
                        institution=edu.get("institution"),
                        graduation_year=edu.get("graduation_year")
                    ))

                # Experience
                for exp in parsed.get("experience", []):
                    db.add(CandidateExperience(
                        candidate_id=candidate.id,
                        title=exp["title"],
                        company=exp.get("company"),
                        duration_years=exp.get("duration_years", 0.0),
                        is_current=exp.get("is_current", False)
                    ))

                db.commit()
                db.refresh(candidate)
                processed_candidates.append(candidate)
                print(f"✓ Parsed candidate: {candidate.name} ({len(parsed['skills'])} skills, {candidate.total_experience_years} yrs exp)")
            else:
                processed_candidates.append(candidate)

        # 4. Run AI Matching Engine for All Jobs
        print("\nExecuting AI Matching Engine across all candidates and job criteria...")
        for job in created_jobs:
            job_data = {
                "title": job.title,
                "description": job.description,
                "required_skills": [s.skill_name for s in job.required_skills],
                "preferred_skills": [s.skill_name for s in job.preferred_skills],
                "min_experience_years": job.min_experience_years,
                "required_education_level": job.required_education_level
            }

            for cand in processed_candidates:
                latest_resume = db.query(Resume).filter(Resume.candidate_id == cand.id).first()
                cand_data = {
                    "skills": [{"skill_name": s.skill_name, "category": s.category} for s in cand.skills],
                    "total_experience_years": cand.total_experience_years,
                    "highest_education_level": cand.highest_education_level,
                    "raw_text": latest_resume.raw_text if latest_resume else ""
                }

                res = matching_engine.calculate_match(candidate_data=cand_data, job_data=job_data)

                match_rec = db.query(MatchResult).filter(
                    MatchResult.job_id == job.id,
                    MatchResult.candidate_id == cand.id
                ).first()

                if not match_rec:
                    match_rec = MatchResult(
                        job_id=job.id,
                        candidate_id=cand.id,
                        overall_score=res["overall_score"],
                        required_skills_score=res["required_skills_score"],
                        preferred_skills_score=res["preferred_skills_score"],
                        experience_score=res["experience_score"],
                        education_score=res["education_score"],
                        text_similarity_score=res["text_similarity_score"],
                        match_tier=res["match_tier"],
                        explanation_report=res["explanation_report"]
                    )
                    db.add(match_rec)
                else:
                    match_rec.overall_score = res["overall_score"]
                    match_rec.match_tier = res["match_tier"]
                    match_rec.explanation_report = res["explanation_report"]

            db.commit()
            print(f"✓ Completed matching calculations for role: {job.title}")

        # 5. Create Initial Shortlist
        first_job = created_jobs[0]
        shortlist = db.query(Shortlist).filter(Shortlist.job_id == first_job.id).first()
        if not shortlist:
            shortlist = Shortlist(
                name="Top Engineering Finalists (Q4)",
                job_id=first_job.id,
                description="Top candidates exhibiting strong mastery of Python, FastAPI, and modern cloud architecture.",
                created_by_id=user.id
            )
            db.add(shortlist)
            db.flush()

            # Add top matching candidates to shortlist
            top_matches = db.query(MatchResult).filter(MatchResult.job_id == first_job.id).order_by(MatchResult.overall_score.desc()).limit(2).all()
            for tm in top_matches:
                db.add(ShortlistCandidate(
                    shortlist_id=shortlist.id,
                    candidate_id=tm.candidate_id,
                    notes="Demonstrates comprehensive full-stack and distributed architecture mastery."
                ))
            db.commit()
            print(f"✓ Created shortlist: {shortlist.name} with {len(top_matches)} candidates")

        print("\n=======================================================")
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print(f"Total Jobs: {db.query(Job).count()}")
        print(f"Total Candidates: {db.query(Candidate).count()}")
        print(f"Total Resumes: {db.query(Resume).count()}")
        print(f"Total Match Results: {db.query(MatchResult).count()}")
        print(f"Total Shortlists: {db.query(Shortlist).count()}")
        print("=======================================================")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
