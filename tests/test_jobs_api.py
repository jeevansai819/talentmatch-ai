def test_create_and_get_job(client, auth_headers):
    # 1. Create Job
    job_payload = {
        "title": "Backend Python Lead",
        "department": "Engineering",
        "location": "Remote",
        "employment_type": "Full-time",
        "min_experience_years": 5.0,
        "required_education_level": "Bachelor",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["Docker", "Kubernetes"],
        "description": "Lead backend development of high concurrency microservices using Python and FastAPI."
    }

    create_res = client.post("/api/jobs", json=job_payload, headers=auth_headers)
    assert create_res.status_code == 201
    job_data = create_res.json()
    assert job_data["title"] == "Backend Python Lead"
    job_id = job_data["id"]

    # 2. Get Job Details
    get_res = client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert len(get_res.json()["required_skills"]) >= 3

    # 3. Update Job
    update_res = client.put(f"/api/jobs/{job_id}", json={"min_experience_years": 6.0}, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["min_experience_years"] == 6.0

    # 4. List Jobs
    list_res = client.get("/api/jobs", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Delete Job
    del_res = client.delete(f"/api/jobs/{job_id}", headers=auth_headers)
    assert del_res.status_code == 204
