from app.services.resume_parser import resume_parser
from app.services.skill_extractor import skill_extractor

def test_skill_extractor_taxonomy():
    text = "Candidate has strong knowledge of Python, FastAPI, React, PostgreSQL, Docker and AWS."
    skills = skill_extractor.extract_skills_from_text(text)
    skill_names = [s["skill_name"] for s in skills]

    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert "React" in skill_names
    assert "PostgreSQL" in skill_names
    assert "Docker" in skill_names
    assert "AWS" in skill_names

def test_resume_parser_structured_extraction():
    raw_resume = """
    Jane Smith
    Email: jane.smith@techcorp.io | Phone: (555) 987-6543 | Location: New York, NY
    LinkedIn: linkedin.com/in/janesmith-dev

    SUMMARY
    Senior Full Stack Engineer with 7+ years of experience building distributed systems.

    SKILLS
    Python, FastAPI, Django, React, PostgreSQL, Redis, Kubernetes, Docker, Git

    EXPERIENCE
    Lead Software Engineer | Apex Solutions (2020 - Present)
    • Architected microservices with FastAPI and PostgreSQL.

    Software Developer | DataWave (2017 - 2020)
    • Developed Django applications.

    EDUCATION
    Master of Science in Computer Science | Columbia University (2017)
    """

    parsed = resume_parser.parse(raw_resume)
    assert parsed["name"] == "Jane Smith"
    assert parsed["email"] == "jane.smith@techcorp.io"
    assert parsed["phone"] == "(555) 987-6543"
    assert parsed["total_experience_years"] >= 6.0
    assert "Master" in parsed["highest_education_level"]

    skills_detected = [s["skill_name"] for s in parsed["skills"]]
    assert "Python" in skills_detected
    assert "FastAPI" in skills_detected
    assert "React" in skills_detected
