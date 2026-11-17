import io
import pymupdf

def test_resume_upload_and_extraction(client, auth_headers):
    # Create sample in-memory PDF
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        """Lucas Gray
        Email: lucas.gray@example.com | Phone: 555-432-1098
        Summary: Full stack developer with 4 years experience in Python, React, and Docker.
        Skills: Python, FastAPI, React, Docker, PostgreSQL
        Experience:
        Software Engineer at CloudTech (2020 - 2024)
        Education:
        Bachelor of Science in Computer Science, University of Michigan (2020)
        """
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    # Upload via API
    files = [
        ("files", ("lucas_gray_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf"))
    ]
    response = client.post("/api/resumes/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["successful_count"] == 1
    assert data["failed_count"] == 0
    assert data["results"][0]["status"] == "success"
    assert data["results"][0]["candidate_name"] == "Lucas Gray"

def test_resume_upload_rejects_non_pdf(client, auth_headers):
    files = [
        ("files", ("malicious_file.exe", io.BytesIO(b"executable content"), "application/octet-stream"))
    ]
    response = client.post("/api/resumes/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["failed_count"] == 1
    assert "only pdf" in data["results"][0]["message"].lower()
