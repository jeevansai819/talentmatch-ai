import re
import math
from collections import Counter
from typing import Dict, Any, List, Set, Tuple, Optional

from app.core.config import settings
from app.utils.constants import DEGREE_HIERARCHY, SCORE_TIERS
from app.utils.helpers import normalize_text

class PurePythonTfidfVectorizer:
    """
    High-performance, pure-Python TF-IDF vectorizer and Cosine Similarity engine.
    Uses exact scikit-learn standard smooth-IDF formulation:
        idf(t) = ln((1 + n) / (1 + df(t))) + 1
        tf(t, d) = count(t, d) / len(d)
        L2 normalization: u = v / ||v||_2
        Cosine similarity: dot(u_1, u_2)
    Guarantees deterministic execution across environments.
    """

    ENGLISH_STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
        "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
        "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
        "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
        "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
        "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
        "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
        "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
        "yours", "yourself", "yourselves"
    }

    def tokenize(self, text: str) -> List[str]:
        """Preprocess and tokenize text, filtering numbers and stopwords."""
        clean = normalize_text(text)
        tokens = re.findall(r'\b[a-zA-Z\+\#]{2,}\b', clean)
        return [t for t in tokens if t not in self.ENGLISH_STOPWORDS]

    def compute_cosine_similarity(self, doc1: str, doc2: str) -> float:
        """Compute cosine similarity between two documents via TF-IDF."""
        tokens1 = self.tokenize(doc1)
        tokens2 = self.tokenize(doc2)

        if not tokens1 or not tokens2:
            return 0.0

        docs = [tokens1, tokens2]
        num_docs = len(docs)

        # Build vocabulary & document frequency
        vocab: Set[str] = set(tokens1).union(set(tokens2))
        df: Dict[str, int] = {}
        for term in vocab:
            df[term] = sum(1 for doc in docs if term in doc)

        # Compute smooth IDF: ln((1 + n) / (1 + df)) + 1
        idf: Dict[str, float] = {
            term: math.log((1.0 + num_docs) / (1.0 + df[term])) + 1.0
            for term in vocab
        }

        # Vectorize both docs
        def vectorize(tokens: List[str]) -> Dict[str, float]:
            counts = Counter(tokens)
            total = len(tokens)
            tfidf = {t: (counts[t] / total) * idf[t] for t in counts}
            # L2 normalize
            norm = math.sqrt(sum(v * v for v in tfidf.values()))
            if norm == 0:
                return {}
            return {t: v / norm for t, v in tfidf.items()}

        vec1 = vectorize(tokens1)
        vec2 = vectorize(tokens2)

        # Dot product
        common_terms = set(vec1.keys()).intersection(set(vec2.keys()))
        similarity = sum(vec1[t] * vec2[t] for t in common_terms)

        return float(min(1.0, max(0.0, similarity)))


class MatchingEngine:
    """
    AI-Powered Resume Matching Engine.
    Implements multi-dimensional weighted compatibility scoring:
      - Required Skills (40%)
      - Preferred Skills (20%)
      - Experience Duration (20%)
      - Education Qualifications (10%)
      - Textual Semantic Similarity (10%)
    """

    def __init__(self):
        self.tfidf_vectorizer = PurePythonTfidfVectorizer()

    def calculate_match(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate compatibility against job requirements and generate explainable report.
        """
        # 1. Scoring Weights
        if weights is None:
            weights = {
                "required_skills": settings.WEIGHT_REQUIRED_SKILLS,
                "preferred_skills": settings.WEIGHT_PREFERRED_SKILLS,
                "experience": settings.WEIGHT_EXPERIENCE,
                "education": settings.WEIGHT_EDUCATION,
                "text_similarity": settings.WEIGHT_TEXT_SIMILARITY
            }
        
        # Normalize weights to ensure 100% total
        total_weight = sum(weights.values())
        norm_weights = {k: v / total_weight for k, v in weights.items()}

        # 2. Extract Candidate Data
        candidate_skills_set = {
            s["skill_name"].lower(): s["skill_name"] 
            for s in candidate_data.get("skills", [])
        }
        cand_exp_years = float(candidate_data.get("total_experience_years") or 0.0)
        cand_education = candidate_data.get("highest_education_level", "Unavailable")
        cand_text = candidate_data.get("raw_text", "")

        # 3. Extract Job Data
        job_req_skills = job_data.get("required_skills", [])
        job_pref_skills = job_data.get("preferred_skills", [])
        job_min_exp = float(job_data.get("min_experience_years") or 0.0)
        job_education = job_data.get("required_education_level", "Bachelor")
        job_description = f"{job_data.get('title', '')} {job_data.get('description', '')}"

        # ----------------------------------------------------
        # Score Component 1: Required Skills Matching (40%)
        # ----------------------------------------------------
        matched_required: List[str] = []
        missing_required: List[str] = []
        
        if job_req_skills:
            for skill in job_req_skills:
                skill_name = skill if isinstance(skill, str) else skill.get("skill_name", "")
                if skill_name.lower() in candidate_skills_set:
                    matched_required.append(skill_name)
                else:
                    # Also check raw text for exact phrase occurrence
                    if re.search(rf'\b{re.escape(skill_name)}\b', cand_text, re.IGNORECASE):
                        matched_required.append(skill_name)
                    else:
                        missing_required.append(skill_name)

            required_score = (len(matched_required) / len(job_req_skills)) * 100.0
        else:
            required_score = 100.0  # No required skills specified

        # ----------------------------------------------------
        # Score Component 2: Preferred Skills Matching (20%)
        # ----------------------------------------------------
        matched_preferred: List[str] = []
        missing_preferred: List[str] = []

        if job_pref_skills:
            for skill in job_pref_skills:
                skill_name = skill if isinstance(skill, str) else skill.get("skill_name", "")
                if skill_name.lower() in candidate_skills_set:
                    matched_preferred.append(skill_name)
                else:
                    if re.search(rf'\b{re.escape(skill_name)}\b', cand_text, re.IGNORECASE):
                        matched_preferred.append(skill_name)
                    else:
                        missing_preferred.append(skill_name)

            preferred_score = (len(matched_preferred) / len(job_pref_skills)) * 100.0
        else:
            # When no preferred skills are listed, give full credit for this component
            preferred_score = 100.0

        # ----------------------------------------------------
        # Score Component 3: Experience Matching (20%)
        # ----------------------------------------------------
        if job_min_exp <= 0:
            exp_score = 100.0
            exp_status = "Meets or exceeds minimum requirements"
        else:
            if cand_exp_years >= job_min_exp:
                exp_score = 100.0
                exp_status = f"{cand_exp_years:.1f} years (Exceeds required {job_min_exp:.1f} yrs)"
            elif cand_exp_years > 0:
                # Pro-rated score
                exp_score = min(100.0, (cand_exp_years / job_min_exp) * 85.0)
                exp_status = f"{cand_exp_years:.1f} years (Required: {job_min_exp:.1f} yrs)"
            else:
                # Experience unavailable
                exp_score = 40.0
                exp_status = f"Not explicitly listed (Required: {job_min_exp:.1f} yrs)"

        # ----------------------------------------------------
        # Score Component 4: Education Matching (10%)
        # ----------------------------------------------------
        job_edu_rank = self._get_degree_rank(job_education)
        cand_edu_rank = self._get_degree_rank(cand_education)

        if cand_edu_rank >= job_edu_rank and cand_edu_rank > 0:
            edu_score = 100.0
            edu_status = f"{cand_education} (Meets required {job_education})"
        elif cand_edu_rank > 0:
            # Candidate has a degree, but lower than required (e.g., Bachelor's vs Master's)
            edu_score = 75.0
            edu_status = f"{cand_education} (Required: {job_education})"
        else:
            # Education level not identified
            edu_score = 50.0
            edu_status = f"Degree unconfirmed (Required: {job_education})"

        # ----------------------------------------------------
        # Score Component 5: Textual / Semantic Similarity (10%)
        # ----------------------------------------------------
        cosine_sim = self.tfidf_vectorizer.compute_cosine_similarity(cand_text, job_description)
        text_score = min(100.0, cosine_sim * 100.0)

        # ----------------------------------------------------
        # Final Weighted Overall Compatibility Score
        # ----------------------------------------------------
        overall = (
            (required_score * norm_weights["required_skills"]) +
            (preferred_score * norm_weights["preferred_skills"]) +
            (exp_score * norm_weights["experience"]) +
            (edu_score * norm_weights["education"]) +
            (text_score * norm_weights["text_similarity"])
        )
        overall_score = round(min(100.0, max(0.0, overall)), 1)

        # Determine Tier
        tier_label = "Low Match"
        if overall_score >= SCORE_TIERS["EXCELLENT"]["min"]:
            tier_label = SCORE_TIERS["EXCELLENT"]["label"]
        elif overall_score >= SCORE_TIERS["STRONG"]["min"]:
            tier_label = SCORE_TIERS["STRONG"]["label"]
        elif overall_score >= SCORE_TIERS["MODERATE"]["min"]:
            tier_label = SCORE_TIERS["MODERATE"]["label"]

        # ----------------------------------------------------
        # Step 7: Explainable Report Generation
        # ----------------------------------------------------
        strengths, gaps, narrative = self._generate_explanation(
            overall_score=overall_score,
            matched_required=matched_required,
            missing_required=missing_required,
            matched_preferred=matched_preferred,
            missing_preferred=missing_preferred,
            cand_exp_years=cand_exp_years,
            job_min_exp=job_min_exp,
            cand_education=cand_education,
            job_education=job_education,
            text_score=text_score
        )

        explanation_report = {
            "overall_match_percentage": overall_score,
            "match_tier": tier_label,
            "score_breakdown": {
                "required_skills": round(required_score, 1),
                "preferred_skills": round(preferred_score, 1),
                "experience": round(exp_score, 1),
                "education": round(edu_score, 1),
                "text_similarity": round(text_score, 1)
            },
            "weights_used": {
                "required_skills": weights["required_skills"],
                "preferred_skills": weights["preferred_skills"],
                "experience": weights["experience"],
                "education": weights["education"],
                "text_similarity": weights["text_similarity"]
            },
            "skills_analysis": {
                "matched_required_skills": matched_required,
                "missing_required_skills": missing_required,
                "matched_preferred_skills": matched_preferred,
                "missing_preferred_skills": missing_preferred,
                "total_skills_detected": len(candidate_skills_set)
            },
            "experience_comparison": {
                "candidate_years": cand_exp_years,
                "required_years": job_min_exp,
                "status": exp_status
            },
            "education_comparison": {
                "candidate_education": cand_education,
                "required_education": job_education,
                "status": edu_status
            },
            "strengths": strengths,
            "potential_gaps": gaps,
            "narrative_explanation": narrative
        }

        return {
            "overall_score": overall_score,
            "required_skills_score": round(required_score, 1),
            "preferred_skills_score": round(preferred_score, 1),
            "experience_score": round(exp_score, 1),
            "education_score": round(edu_score, 1),
            "text_similarity_score": round(text_score, 1),
            "match_tier": tier_label,
            "explanation_report": explanation_report
        }

    def _get_degree_rank(self, degree_str: str) -> int:
        """Map degree text to normalized hierarchical rank 1-5."""
        if not degree_str:
            return 0
        d_lower = degree_str.lower()
        for key, rank in DEGREE_HIERARCHY.items():
            if key in d_lower:
                return rank
        return 2  # Default baseline for unrecognized qualification

    def _generate_explanation(
        self,
        overall_score: float,
        matched_required: List[str],
        missing_required: List[str],
        matched_preferred: List[str],
        missing_preferred: List[str],
        cand_exp_years: float,
        job_min_exp: float,
        cand_education: str,
        job_education: str,
        text_score: float
    ) -> Tuple[List[str], List[str], str]:
        """Synthesize explainable recruiter strengths, gaps, and narrative."""
        strengths: List[str] = []
        gaps: List[str] = []

        # Skills breakdown
        if matched_required:
            strengths.append(f"Possesses core required skills: {', '.join(matched_required[:5])}.")
        if matched_preferred:
            strengths.append(f"Demonstrates bonus preferred proficiencies: {', '.join(matched_preferred[:4])}.")
        if missing_required:
            gaps.append(f"Missing mandatory required skills: {', '.join(missing_required[:5])}.")

        # Experience breakdown
        if cand_exp_years >= job_min_exp and job_min_exp > 0:
            strengths.append(f"Experience level ({cand_exp_years:.1f} yrs) satisfies the required {job_min_exp:.1f} years.")
        elif job_min_exp > 0 and cand_exp_years < job_min_exp:
            gaps.append(f"Experience duration ({cand_exp_years:.1f} yrs) falls short of target {job_min_exp:.1f} years.")

        # Education breakdown
        if self._get_degree_rank(cand_education) >= self._get_degree_rank(job_education):
            strengths.append(f"Holds required academic credentials ({cand_education}).")
        elif cand_education != "Unavailable":
            gaps.append(f"Academic background ({cand_education}) differs from target {job_education}.")

        # Narrative explanation
        if overall_score >= 85:
            summary = (
                f"Candidate exhibits an outstanding alignment ({overall_score}%) with the role. "
                f"Strong proficiency demonstrated across key requirements with "
                f"{len(matched_required)} of {len(matched_required) + len(missing_required)} core skills satisfied."
            )
        elif overall_score >= 70:
            summary = (
                f"Candidate shows solid compatibility ({overall_score}%). "
                f"Matches major technical competencies with minor gaps in specific tools or experience."
            )
        elif overall_score >= 50:
            summary = (
                f"Candidate demonstrates moderate potential ({overall_score}%). "
                f"Possesses transferable background, but lacks several key requirements that may require onboarding training."
            )
        else:
            summary = (
                f"Candidate displays low alignment ({overall_score}%) with the role criteria. "
                f"Notable divergences exist in primary technical stacks and experience expectations."
            )

        return strengths, gaps, summary

matching_engine = MatchingEngine()
