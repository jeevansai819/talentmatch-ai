import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.skill_extractor import skill_extractor
from app.utils.constants import DEGREE_HIERARCHY
from app.utils.helpers import (
    extract_email,
    extract_phone,
    extract_links,
    extract_experience_years_from_text,
    YEAR_REGEX
)

class ResumeParser:
    """Robust resume parser extracting candidate details, education, experience, and skills."""

    EDUCATION_DEGREES = [
        ("Ph.D.", ["ph.d", "phd", "doctor of philosophy", "doctorate"]),
        ("Master's Degree", ["master of science", "master of arts", "m.sc", "msc", "m.s.", "ms in", "m.tech", "mtech", "mba", "mca", "master's", "masters"]),
        ("Bachelor's Degree", ["bachelor of science", "bachelor of engineering", "bachelor of technology", "b.sc", "bsc", "b.tech", "btech", "b.e.", "b.s.", "bca", "bba", "bachelor's", "bachelors"]),
        ("Associate Degree", ["associate degree", "associate of science", "associate of arts", "diploma"]),
        ("High School", ["high school", "secondary school", "higher secondary", "12th grade"])
    ]

    def parse(self, raw_text: str) -> Dict[str, Any]:
        """Parse raw resume text into structured candidate records."""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        # 1. Contact Info
        email = extract_email(raw_text)
        phone = extract_phone(raw_text)
        links = extract_links(raw_text)
        location = self._extract_location(raw_text)

        # 2. Candidate Name
        name = self._extract_candidate_name(lines, email)

        # 3. Skills
        skills = skill_extractor.extract_skills_from_text(raw_text)

        # 4. Education Records & Highest Education
        education_records, highest_education = self._extract_education(raw_text)

        # 5. Experience Records & Total Years
        experience_records, total_years = self._extract_experience(raw_text)

        # 6. Projects & Certifications
        projects = self._extract_projects(raw_text)
        certifications = self._extract_certifications(raw_text)

        # 7. Professional Summary
        summary = self._extract_summary(raw_text, lines)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin_url": links.get("linkedin"),
            "github_url": links.get("github"),
            "summary": summary,
            "total_experience_years": total_years,
            "highest_education_level": highest_education,
            "skills": skills,
            "education": education_records,
            "experience": experience_records,
            "projects": projects,
            "certifications": certifications,
            "raw_text": raw_text
        }

    def _extract_candidate_name(self, lines: List[str], email: Optional[str]) -> str:
        """Heuristic name extractor from header lines with email fallback."""
        for line in lines[:6]:
            clean_line = re.sub(r'[\r\n,]+', ' ', line).strip()
            # Remove trailing academic suffixes like Ph.D., M.S., B.Tech, etc.
            clean_name = re.sub(r'\b(Ph\.?D\.?|M\.?S\.?|B\.?S\.?|M\.?B\.?A\.?|M\.?Tech|B\.?Tech|P\.?E\.?)\b', '', clean_line, flags=re.IGNORECASE).strip()
            clean_name = re.sub(r'\s+', ' ', clean_name).strip()

            # Filter out obvious header noise
            if any(term in clean_name.lower() for term in ["resume", "curriculum", "cv", "page", "email", "phone", "http", "@", ".com", "summary", "profile", "objective"]):
                continue
            words = clean_name.split()
            # Most names are 2 to 4 capitalized words without digits
            if 1 < len(words) <= 4 and all(re.match(r'^[A-Z][a-zA-Z\.\'-]*$', w) for w in words):
                return clean_name

        # If header didn't give clear name, check email local part (e.g. john.doe@email.com)
        if email:
            local = email.split("@")[0]
            clean_local = re.sub(r'[\d._-]+', ' ', local).title().strip()
            if len(clean_local.split()) >= 2:
                return clean_local

        # Fallback to first non-empty line or generic
        return lines[0][:50] if lines else "Candidate"

    def _extract_location(self, text: str) -> Optional[str]:
        """Detect city, state or country locations from header."""
        location_regex = re.compile(
            r'\b(?:Location|Address|Based in|City)?[:\s\-]*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z]+)?)\b'
        )
        # Search primarily in first 1000 characters
        header_text = text[:1000]
        matches = location_regex.findall(header_text)
        for loc in matches:
            if not any(skip in loc.lower() for skip in ["resume", "curriculum", "email", "phone", "university", "school", "college"]):
                if len(loc.split()) <= 3 and len(loc) > 3:
                    return loc.strip()
        return None

    def _extract_education(self, text: str) -> tuple[List[Dict[str, Any]], str]:
        """Extract degree qualifications, university, and graduation year."""
        records = []
        highest = "Unavailable"
        highest_rank = 0

        # Scan for recognized degree categories
        text_lower = text.lower()
        for formal_degree, variants in self.EDUCATION_DEGREES:
            for variant in variants:
                if re.search(rf'\b{re.escape(variant)}\b', text_lower):
                    # Check rank
                    rank = DEGREE_HIERARCHY.get(formal_degree.split()[0].lower(), 2)
                    if rank > highest_rank:
                        highest_rank = rank
                        highest = formal_degree

                    # Try to find associated year
                    year_match = YEAR_REGEX.search(text)
                    grad_year = int(year_match.group(0)) if year_match else None

                    # Try to find institution name around the degree
                    institution = self._find_institution(text)

                    records.append({
                        "degree": formal_degree,
                        "field_of_study": self._find_field_of_study(text),
                        "institution": institution,
                        "graduation_year": grad_year
                    })
                    break  # One match per degree group

        if not records and highest == "Unavailable":
            # Check for general keywords
            if "bachelor" in text_lower or "b.tech" in text_lower or "b.e." in text_lower:
                highest = "Bachelor's Degree"
            elif "master" in text_lower or "m.tech" in text_lower:
                highest = "Master's Degree"

        return records, highest

    def _find_institution(self, text: str) -> Optional[str]:
        """Detect University/College name."""
        match = re.search(
            r'([A-Z][a-zA-Z\s]+(?:University|Institute of Technology|College|Academy|State University|School of [A-Za-z]+))',
            text
        )
        return match.group(0).strip() if match else None

    def _find_field_of_study(self, text: str) -> Optional[str]:
        """Detect common majors."""
        match = re.search(
            r'\b(?:in|of)\s+((?:Computer Science|Data Science|Software Engineering|Information Technology|Electrical Engineering|Mechanical Engineering|Business Administration|Artificial Intelligence|Cybersecurity))\b',
            text,
            re.IGNORECASE
        )
        return match.group(1).title() if match else None

    def _extract_experience(self, text: str) -> tuple[List[Dict[str, Any]], float]:
        """Extract job titles, companies, and total years of experience."""
        total_years = extract_experience_years_from_text(text)
        records = []

        # Find experience section
        exp_section_match = re.search(
            r'(?:work experience|professional experience|experience|employment history)([\s\S]{100,2500}?)(?=(?:education|skills|projects|certifications|$))',
            text,
            re.IGNORECASE
        )
        section_text = exp_section_match.group(1) if exp_section_match else text

        # Search for job title patterns
        job_title_regex = re.compile(
            r'\b((?:Senior\s+|Junior\s+|Lead\s+|Principal\s+|Staff\s+)?(?:Software Engineer|Developer|Data Scientist|DevOps Engineer|Frontend Developer|Backend Developer|Full Stack Developer|Product Manager|System Architect|Analyst|Intern))\b',
            re.IGNORECASE
        )
        matches = job_title_regex.finditer(section_text)
        for m in matches:
            title = m.group(1).title()
            records.append({
                "title": title,
                "company": "Company",
                "duration_years": round(total_years / max(1, len(records) + 1), 1),
                "is_current": "present" in section_text.lower(),
                "description": None
            })

        return records[:5], total_years

    def _extract_projects(self, text: str) -> List[str]:
        """Extract project names or bullet points under projects section."""
        match = re.search(r'(?:projects|personal projects)([\s\S]{50,1000}?)(?=(?:skills|education|experience|certifications|$))', text, re.IGNORECASE)
        if not match:
            return []
        proj_lines = [line.strip().lstrip('•-*· ') for line in match.group(1).splitlines() if len(line.strip()) > 15]
        return proj_lines[:4]

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications (e.g. AWS Certified, CKA, PMP)."""
        certs = []
        cert_patterns = [
            r'AWS Certified [A-Za-z\s]+',
            r'Azure Solutions Architect',
            r'Google Cloud Certified [A-Za-z\s]+',
            r'Certified Kubernetes Administrator',
            r'PMP|Project Management Professional',
            r'Scrum Master|CSM'
        ]
        for p in cert_patterns:
            found = re.findall(p, text, re.IGNORECASE)
            for f in found:
                if f.title() not in certs:
                    certs.append(f.title())
        return certs

    def _extract_summary(self, raw_text: str, lines: List[str]) -> Optional[str]:
        """Extract 1-3 sentence profile summary."""
        match = re.search(r'(?:summary|profile|about me|objective)[:\s\-]+([\s\S]{50,400}?)(?=(?:skills|experience|education|$))', raw_text, re.IGNORECASE)
        if match:
            return re.sub(r'\s+', ' ', match.group(1)).strip()
        # Fallback to first paragraph after header
        for line in lines[1:6]:
            if len(line) > 60 and not any(skip in line.lower() for skip in ["http", "@", "skills", "experience"]):
                return line.strip()
        return None

resume_parser = ResumeParser()
