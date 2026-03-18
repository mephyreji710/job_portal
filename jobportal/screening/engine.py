"""
Scoring engine for Module 6: Smart Resume Screening.

Weights:
  Skills Match     40%
  Experience       25%
  Education        15%
  Keyword Relevance 20%
"""

import re
from datetime import date

WEIGHTS = {
    'skills':     0.40,
    'experience': 0.25,
    'education':  0.15,
    'keywords':   0.20,
}

# Numeric rank for education levels (shared vocabulary across apps)
EDUCATION_RANK = {
    'high_school': 1,
    'diploma':     2,
    'associate':   2,
    'certificate': 2,
    'bachelor':    3,
    'master':      4,
    'phd':         5,
}

STOP_WORDS = {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
    'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
    'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'any',
    'this', 'that', 'with', 'have', 'from', 'they', 'will', 'been', 'more',
    'when', 'there', 'than', 'then', 'some', 'what', 'into', 'time', 'very',
    'just', 'also', 'well', 'over', 'such', 'team', 'work', 'must', 'good',
    'high', 'keep', 'make', 'plus', 'role', 'both', 'each', 'like', 'need',
    'your', 'come', 'data', 'help', 'here', 'know', 'look', 'only', 'open',
    'same', 'take', 'them', 'used', 'using', 'years', 'year', 'strong',
    'skills', 'skill', 'experience', 'required', 'preferred', 'including',
    'ability', 'working', 'provide', 'position', 'minimum', 'candidate',
    'responsibilities', 'requirements', 'qualification', 'qualifications',
}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_job_keywords(job):
    """Return a set of meaningful lowercase words from the job posting."""
    text = ' '.join([
        job.title,
        job.description or '',
        job.requirements or '',
        job.responsibilities or '',
        job.required_skills or '',     # include required skills field
    ]).lower()
    words = re.findall(r'[a-z][a-z0-9+#.]*', text)
    # min length 2 so short but important skills (aws, go, r, c#) are kept
    return {w for w in words if len(w) >= 2 and w not in STOP_WORDS}


def _get_candidate_skills(js_profile, parsed_resume):
    """Return a set of lowercase skill names from profile + resume."""
    skills = set()
    if js_profile:
        for s in js_profile.skills.all():
            skills.add(s.name.lower().strip())
    if parsed_resume:
        for item in parsed_resume.extracted_skills:
            name = item.get('name', '') if isinstance(item, dict) else str(item)
            if name:
                skills.add(name.lower().strip())
    return skills


def _score_skills(job, js_profile, parsed_resume):
    required = {s.lower() for s in job.get_skills_list()}
    if not required:
        return 100.0, [], []
    candidate = _get_candidate_skills(js_profile, parsed_resume)
    matched = sorted(required & candidate)
    missing = sorted(required - candidate)
    score = len(matched) / len(required) * 100
    return min(score, 100.0), matched, missing


def _get_candidate_experience_years(js_profile, parsed_resume):
    """Total experience years from profile records and/or resume estimate."""
    years = 0.0
    if js_profile:
        for exp in js_profile.experience.all():
            end = date.today() if exp.is_current else (exp.end_date or date.today())
            months = ((end.year - exp.start_date.year) * 12
                      + end.month - exp.start_date.month)
            years += max(0, months) / 12
    if parsed_resume and parsed_resume.estimated_experience_years:
        years = max(years, parsed_resume.estimated_experience_years)
    return round(years, 1)


def _score_experience(job, js_profile, parsed_resume):
    required_min = job.experience_years_min or 0
    candidate_years = _get_candidate_experience_years(js_profile, parsed_resume)
    if required_min == 0:
        return 100.0, candidate_years
    score = min(candidate_years / required_min * 100, 100.0)
    return score, candidate_years


def _get_candidate_edu_rank(js_profile, parsed_resume):
    """Return highest education rank found across profile + resume."""
    rank = 0
    if js_profile:
        for edu in js_profile.education.all():
            rank = max(rank, EDUCATION_RANK.get(edu.degree, 0))
    if parsed_resume and parsed_resume.education_level:
        rank = max(rank, EDUCATION_RANK.get(parsed_resume.education_level, 0))
    return rank


def _score_education(job, js_profile, parsed_resume):
    if job.education_required == 'any':
        edu_rank = _get_candidate_edu_rank(js_profile, parsed_resume)
        return 100.0, edu_rank
    required_rank = EDUCATION_RANK.get(job.education_required, 0)
    if required_rank == 0:
        return 100.0, 0
    edu_rank = _get_candidate_edu_rank(js_profile, parsed_resume)
    if edu_rank >= required_rank:
        return 100.0, edu_rank
    if edu_rank == 0:
        return 0.0, 0
    return edu_rank / required_rank * 100, edu_rank


def _get_candidate_keywords(js_profile, parsed_resume):
    """Return a set of lowercase keyword strings the candidate has.

    Pulls from:
    - Profile skills (most reliable — manually entered)
    - Resume extracted_skills (JSON list from parser)
    - Resume ExtractedKeyword rows (word-frequency table)
    - Resume raw_text words (broad fallback)
    """
    words = set()

    # Profile skills
    if js_profile:
        for s in js_profile.skills.all():
            for part in s.name.lower().split():
                words.add(part)
            words.add(s.name.lower().strip())   # also add multi-word as-is

    if parsed_resume:
        # Structured extracted skills
        for item in parsed_resume.extracted_skills:
            name = item.get('name', '') if isinstance(item, dict) else str(item)
            if name:
                words.add(name.lower().strip())
                for part in name.lower().split():
                    words.add(part)

        # Keyword frequency table
        for kw in parsed_resume.keywords.all():
            words.add(kw.word.lower())

        # JSON keyword field
        for item in parsed_resume.extracted_keywords:
            w = item.get('word', '') if isinstance(item, dict) else str(item)
            if w:
                words.add(w.lower())

        # Raw text words as broad fallback (filtered to length >= 3)
        if parsed_resume.resume.raw_text:
            import re as _re
            raw_words = _re.findall(r'[a-z][a-z0-9+#.]*',
                                    parsed_resume.resume.raw_text.lower())
            words.update(w for w in raw_words if len(w) >= 3)

    return words


def _score_keywords(job, js_profile, parsed_resume):
    job_keywords = _extract_job_keywords(job)
    if not job_keywords:
        return 100.0, []
    candidate_kw = _get_candidate_keywords(js_profile, parsed_resume)
    matched = sorted(job_keywords & candidate_kw)
    score = len(matched) / len(job_keywords) * 100
    return min(score, 100.0), matched[:30]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_match(job, user):
    """
    Compute the match score for a (job, user) pair.
    Returns a dict with component scores and breakdown details.
    """
    js_profile = None
    parsed_resume = None

    try:
        js_profile = user.js_profile
    except Exception:
        pass

    # Prefer the primary parsed resume; fall back to any parsed resume
    primary = user.resumes.filter(is_primary=True, status='parsed').first()
    if not primary:
        primary = user.resumes.filter(status='parsed').first()
    if primary:
        try:
            parsed_resume = primary.parsed
        except Exception:
            pass

    skills_score, matched_skills, missing_skills = _score_skills(job, js_profile, parsed_resume)
    exp_score, exp_years = _score_experience(job, js_profile, parsed_resume)
    edu_score, edu_rank = _score_education(job, js_profile, parsed_resume)
    kw_score, matched_keywords = _score_keywords(job, js_profile, parsed_resume)

    total = (
        skills_score * WEIGHTS['skills'] +
        exp_score    * WEIGHTS['experience'] +
        edu_score    * WEIGHTS['education'] +
        kw_score     * WEIGHTS['keywords']
    )

    return {
        'skills_score':          round(skills_score, 1),
        'experience_score':      round(exp_score, 1),
        'education_score':       round(edu_score, 1),
        'keywords_score':        round(kw_score, 1),
        'total_score':           round(total, 1),
        'matched_skills':        matched_skills,
        'missing_skills':        missing_skills,
        'matched_keywords':      matched_keywords,
        'experience_years_found': exp_years,
        'education_rank_found':   edu_rank,
    }
