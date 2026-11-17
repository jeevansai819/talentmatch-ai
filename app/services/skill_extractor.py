import re
from typing import List, Dict, Set, Any
from app.utils.constants import TECHNICAL_SKILLS_TAXONOMY, CANONICAL_SKILL_MAP

class SkillExtractor:
    """Intelligent Skill Extraction Service with multi-word matching & canonicalization."""

    def __init__(self):
        # Precompile regex matchers for skills to ensure fast boundary matching
        self.skill_patterns = []
        for raw_skill, info in CANONICAL_SKILL_MAP.items():
            escaped = re.escape(raw_skill)
            # Match boundary: do not match inside words, but allow sentence punctuation like '.' or ',' at the end
            pattern = re.compile(rf'(?<![a-zA-Z0-9\+#]){escaped}(?![a-zA-Z0-9\+#]|(\.(?=[a-zA-Z0-9])))', re.IGNORECASE)
            self.skill_patterns.append((raw_skill, pattern, info["canonical"], info["category"]))

    def extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Scan text for all recognized technical and domain skills.
        Returns a list of dicts with:
            - skill_name: canonical name (e.g. 'PostgreSQL', 'Docker')
            - category: category name
            - confidence_score: float (1.0 for exact matches)
        """
        if not text:
            return []

        found_skills: Dict[str, Dict[str, Any]] = {}

        # 1. Dictionary & Pattern scan
        for raw_skill, pattern, canonical_name, category in self.skill_patterns:
            if pattern.search(text):
                # Use canonical name as unique key to prevent duplicates
                if canonical_name not in found_skills:
                    found_skills[canonical_name] = {
                        "skill_name": canonical_name,
                        "category": category,
                        "confidence_score": 1.0
                    }

        # 2. Extract any comma-separated or bulleted skill section specifically
        section_skills = self._extract_from_skills_section(text)
        for s in section_skills:
            if s["skill_name"] not in found_skills:
                found_skills[s["skill_name"]] = s

        # Return sorted by category and skill name
        return sorted(list(found_skills.values()), key=lambda x: (x["category"], x["skill_name"]))

    def _extract_from_skills_section(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills listed explicitly under headers like 'SKILLS', 'TECHNICAL PROFICIENCIES'."""
        section_regex = re.compile(
            r'(?:technical\s+skills|skills\s+and\s+competencies|skills|technologies|proficiencies|tech\s+stack)[\s\:\-]+([^\n\r]+(?:\n[^\n\r]+){1,10})',
            re.IGNORECASE
        )
        matches = section_regex.findall(text)
        extracted = []
        for block in matches:
            # Tokenize by comma, pipe, semicolon, bullet
            items = re.split(r'[,\|;•·\n\r/]+', block)
            for item in items:
                clean_item = item.strip().lower()
                clean_item = re.sub(r'^[^\w\+\#\.]+|[^\w\+\#\.]+$', '', clean_item)
                if clean_item in CANONICAL_SKILL_MAP:
                    info = CANONICAL_SKILL_MAP[clean_item]
                    extracted.append({
                        "skill_name": info["canonical"],
                        "category": info["category"],
                        "confidence_score": 1.0
                    })
        return extracted

    def normalize_skill_list(self, raw_skills: List[str]) -> List[str]:
        """Convert a list of raw user-input skill strings to canonical names."""
        canonical_list = []
        seen = set()
        for item in raw_skills:
            key = item.strip().lower()
            if key in CANONICAL_SKILL_MAP:
                canon = CANONICAL_SKILL_MAP[key]["canonical"]
            else:
                canon = item.strip().title()
            if canon and canon not in seen:
                seen.add(canon)
                canonical_list.append(canon)
        return canonical_list

skill_extractor = SkillExtractor()
