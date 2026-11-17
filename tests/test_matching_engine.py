from app.services.matching_engine import matching_engine

def test_matching_engine_high_compatibility():
    candidate_data = {
        "skills": [
            {"skill_name": "Python", "category": "Languages"},
            {"skill_name": "FastAPI", "category": "Backend"},
            {"skill_name": "PostgreSQL", "category": "Databases"},
            {"skill_name": "Docker", "category": "DevOps"},
            {"skill_name": "AWS", "category": "Cloud"}
        ],
        "total_experience_years": 5.0,
        "highest_education_level": "Master's Degree",
        "raw_text": "Experienced Python and FastAPI backend engineer working with PostgreSQL, Docker and AWS cloud deployments."
    }

    job_data = {
        "title": "Senior Python Developer",
        "description": "Looking for a Senior Python Developer experienced with FastAPI, PostgreSQL and Docker.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["Docker", "AWS"],
        "min_experience_years": 4.0,
        "required_education_level": "Bachelor"
    }

    result = matching_engine.calculate_match(candidate_data, job_data)

    assert result["overall_score"] >= 85.0
    assert result["match_tier"] in ["Excellent Match", "Strong Match"]
    assert result["required_skills_score"] == 100.0
    assert result["preferred_skills_score"] == 100.0
    assert result["experience_score"] == 100.0
    assert result["education_score"] == 100.0
    assert "narrative_explanation" in result["explanation_report"]
    assert len(result["explanation_report"]["strengths"]) > 0

def test_matching_engine_low_compatibility():
    candidate_data = {
        "skills": [
            {"skill_name": "HTML", "category": "Frontend"},
            {"skill_name": "CSS", "category": "Frontend"}
        ],
        "total_experience_years": 1.0,
        "highest_education_level": "High School",
        "raw_text": "Entry level web designer with basic HTML and CSS skills."
    }

    job_data = {
        "title": "Staff Cloud Infrastructure Engineer",
        "description": "Enterprise Kubernetes and Terraform cloud architect.",
        "required_skills": ["Kubernetes", "Terraform", "AWS", "Linux"],
        "preferred_skills": ["Ansible", "Golang"],
        "min_experience_years": 8.0,
        "required_education_level": "Bachelor"
    }

    result = matching_engine.calculate_match(candidate_data, job_data)

    assert result["overall_score"] < 50.0
    assert result["match_tier"] == "Low Match"
    assert len(result["explanation_report"]["potential_gaps"]) > 0
