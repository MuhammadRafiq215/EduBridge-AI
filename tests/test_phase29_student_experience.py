from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_subject_catalogue_exposes_subject_families_and_multiple_jurisdictions():
    payload = json.loads((ROOT / "data" / "knowledge" / "subject_catalog.json").read_text(encoding="utf-8"))
    assert len(payload["subject_groups"]) >= 8
    assert len(payload["catalogues"]) >= 8
    assert {"Mathematics and Statistics", "Sciences", "Computing and Technology"}.issubset(payload["subject_groups"])
    assert all(row["subjects"] for row in payload["catalogues"])


def test_subject_catalogue_ui_has_search_and_subject_family_filter():
    page = (ROOT / "pages" / "3_Subject_Catalogue.py").read_text(encoding="utf-8")
    assert "Search subjects" in page
    assert "Explore a subject family" in page
    assert "All subject families" in page
    assert "Historical reference" in page


def test_career_pathways_offer_direct_next_steps():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "career_open_ai_teacher" in app
    assert "career_open_study_planner" in app
    assert "career_compare_pathways" in app


def test_global_knowledge_hub_does_not_expose_research_pending_label():
    page = (ROOT / "pages" / "1_Global_Knowledge_Hub.py").read_text(encoding="utf-8")
    assert "Research pending" not in page
