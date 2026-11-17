def test_analytics_dashboard_metrics(client, auth_headers):
    response = client.get("/api/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "total_resumes" in data
    assert "total_active_jobs" in data
    assert "total_candidates" in data
    assert "total_shortlisted" in data
    assert "average_matching_score" in data
    assert "skills_distribution" in data
    assert "experience_distribution" in data
    assert "education_distribution" in data
    assert "match_score_distribution" in data
    assert "recent_activity" in data
    assert "status_distribution" in data
