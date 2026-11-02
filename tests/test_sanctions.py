import pytest

from aml_triage.sanctions import normalize_name, screen_name


SANCTIONS_NAMES = [
    "Vladimir Example",
    "ABC Trading Ltd",
    "Northstar Exports",
]


def test_exact_name_match():
    results = screen_name("Vladimir Example", SANCTIONS_NAMES)

    assert len(results) >= 1
    assert results[0].matched_name == "Vladimir Example"
    assert results[0].match_type == "EXACT"
    assert results[0].score == 100.0


def test_case_and_whitespace_are_normalized():
    assert normalize_name("  ABC   TRADING LTD ") == "abc trading ltd"

    results = screen_name("  ABC   TRADING LTD ", SANCTIONS_NAMES)

    assert results[0].matched_name == "ABC Trading Ltd"
    assert results[0].match_type == "EXACT"


def test_spelling_variation_can_match():
    results = screen_name(
        "Vladmir Example",
        SANCTIONS_NAMES,
        threshold=80.0,
    )

    assert any(
        result.matched_name == "Vladimir Example"
        and result.match_type == "FUZZY"
        for result in results
    )


def test_unrelated_name_is_not_returned():
    results = screen_name(
        "Completely Different Person",
        SANCTIONS_NAMES,
        threshold=85.0,
    )

    assert results == []


def test_empty_sanctions_list_returns_no_matches():
    assert screen_name("Vladimir Example", []) == []


def test_empty_input_name_is_rejected():
    with pytest.raises(ValueError):
        screen_name("   ", SANCTIONS_NAMES)


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        screen_name("Vladimir Example", SANCTIONS_NAMES, threshold=101)


def test_results_are_sorted_by_score():
    results = screen_name(
        "Vladimir Example",
        [
            "Vladimir Example",
            "Vladimir Examples",
            "Northstar Exports",
        ],
        threshold=50.0,
    )

    scores = [result.score for result in results]
    assert scores == sorted(scores, reverse=True)


def test_fuzzy_match_is_not_mislabeled_as_exact_match():
    results = screen_name(
        "Vladmir Example",
        ["Vladimir Example"],
        threshold=80.0,
    )

    assert len(results) == 1
    assert results[0].match_type == "FUZZY"
    assert results[0].matched_name == "Vladimir Example"
    assert results[0].score < 100.0
