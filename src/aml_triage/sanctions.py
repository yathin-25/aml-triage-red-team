from dataclasses import dataclass
from rapidfuzz import fuzz, process


@dataclass
class SanctionsMatch:
    input_name: str
    matched_name: str
    score: float
    match_type: str


def normalize_name(name: str) -> str:
    """Normalize a name for more consistent comparisons."""
    return " ".join(name.casefold().strip().split())


def screen_name(
    input_name: str,
    sanctions_names: list[str],
    threshold: float = 85.0,
) -> list[SanctionsMatch]:
    """
    Compare a name against a supplied sanctions-name list.

    The threshold is a similarity score, not a probability that
    a person is sanctioned.
    """
    if not 0 <= threshold <= 100:
        raise ValueError("threshold must be between 0 and 100.")

    if not input_name.strip():
        raise ValueError("input_name cannot be empty.")

    normalized_input = normalize_name(input_name)
    normalized_names = {
        normalize_name(name): name
        for name in sanctions_names
        if name.strip()
    }

    if not normalized_names:
        return []

    matches = process.extract(
        normalized_input,
        list(normalized_names.keys()),
        scorer=fuzz.ratio,
        score_cutoff=threshold,
        limit=None,
    )

    results = []

    for matched_normalized, score, _ in matches:
        original_name = normalized_names[matched_normalized]
        match_type = (
            "EXACT"
            if normalized_input == matched_normalized
            else "FUZZY"
        )

        results.append(
            SanctionsMatch(
                input_name=input_name,
                matched_name=original_name,
                score=round(float(score), 2),
                match_type=match_type,
            )
        )

    return sorted(results, key=lambda result: result.score, reverse=True)