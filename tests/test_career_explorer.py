from src.student_guidance import PATHWAYS, search_pathways


def test_career_catalogue_covers_broad_sectors_and_has_complete_entries():
    expected = {
        "Engineering", "Computer Science & AI", "Medicine & Health Sciences",
        "Agriculture & Food Systems", "Energy & Environmental Science",
        "Finance & Accounting", "Law, Policy & International Relations",
        "Media, Communication & Journalism", "Hospitality, Events & Tourism",
        "Manufacturing, Robotics & Automation", "Cybersecurity & Networks",
        "Transportation & Logistics", "Education & Learning Sciences",
        "Sports Science & Human Performance", "Public Service & Community Development",
        "Veterinary & Animal Sciences",
    }
    assert expected.issubset(PATHWAYS)
    for name, item in PATHWAYS.items():
        assert item["description"].strip()
        assert len(item["focus"]) >= 3
        assert len(item["degrees"]) >= 3
        assert len(item["projects"]) >= 3
        assert all(label and url.startswith("https://") for label, url in item["resources"])


def test_search_pathways_finds_subject_related_sectors():
    matches = search_pathways(subjects=["Mathematics", "Physics"])
    assert "Engineering" in matches
    assert "Energy & Environmental Science" in matches
    assert "Finance & Accounting" in matches


def test_search_pathways_supports_text_search_and_combined_filters():
    assert "Cybersecurity & Networks" in search_pathways("cyber")
    assert search_pathways("cyber", ["Biology"]) == []
    assert search_pathways("cyber", ["Computer Science"]) == ["Cybersecurity & Networks"]


def test_search_pathways_empty_query_returns_all_sectors():
    assert search_pathways() == list(PATHWAYS)
