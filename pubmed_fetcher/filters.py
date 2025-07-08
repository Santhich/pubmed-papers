def is_non_academic(affiliation: str) -> bool:
    """Heuristic: Treat affiliation as non-academic if no university keywords."""
    academic_keywords = ["University", "College", "Institute", "Laboratory", "Hospital"]
    return not any(keyword.lower() in affiliation.lower() for keyword in academic_keywords)

