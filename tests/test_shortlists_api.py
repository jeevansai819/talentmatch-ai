from app.models.candidate import Candidate
from app.models.job import Job

def test_shortlist_lifecycle_and_csv_export(client, db, auth_headers, test_user):
    # 1. Create a job
    job = Job(
        title="Frontend Specialist",
        description="React developer with Tailwind experience",
        created_by_id=test_user.id
    )
    db.add(job)

    # 2. Create a candidate
    candidate = Candidate(
        name="Samantha Miller",
        email="samantha@example.com",
        total_experience_years=3.0,
        highest_education_level="Bachelor's Degree",
        current_status="New"
    )
    db.add(candidate)
    db.commit()

    # 3. Create Shortlist
    shortlist_res = client.post(
        "/api/shortlists",
        json={"name": "Frontend Finalists", "job_id": job.id, "description": "Candidate cohort"},
        headers=auth_headers
    )
    assert shortlist_res.status_code == 201
    shortlist_id = shortlist_res.json()["id"]

    # 4. Add Candidate to Shortlist
    add_cand_res = client.post(
        f"/api/shortlists/{shortlist_id}/candidates",
        json={"candidate_id": candidate.id, "notes": "Great React developer"},
        headers=auth_headers
    )
    assert add_cand_res.status_code == 200

    # 5. Export Shortlist as CSV
    csv_res = client.get(f"/api/shortlists/{shortlist_id}/export/csv", headers=auth_headers)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Samantha Miller" in csv_res.text
    assert "Frontend Finalists" in csv_res.text

    # 6. Remove Candidate from Shortlist
    del_cand_res = client.delete(
        f"/api/shortlists/{shortlist_id}/candidates/{candidate.id}",
        headers=auth_headers
    )
    assert del_cand_res.status_code == 204
