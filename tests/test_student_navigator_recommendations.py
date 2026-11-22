from src.student_navigator import build_navigation_plan, build_student_snapshot


def test_snapshot_uses_only_recent_user_questions():
    history = [
        {"role": "user", "content": f"Question {index}"}
        for index in range(7)
    ] + [{"role": "assistant", "content": "Do not include this answer"}]
    snapshot = build_student_snapshot(
        {"subjects": ["Mathematics"], "confidence": {"Mathematics": 2}},
        history,
    )
    assert snapshot["recent_questions"] == [
        "Question 3", "Question 4", "Question 5", "Question 6"
    ]
    assert snapshot["subjects"] == ["Mathematics"]


def test_low_self_reported_confidence_produces_a_clear_subject_priority():
    snapshot = {
        "subjects": ["Mathematics", "Computer Science"],
        "confidence": {"Mathematics": 2, "Computer Science": 4},
        "recent_questions": [],
    }
    plan = build_navigation_plan(snapshot)
    assert "Mathematics" in plan[0]["title"]
    assert "confidence" in plan[0]["reason"].lower()


def test_explicit_focus_takes_priority_over_other_subjects():
    snapshot = {
        "subjects": ["Mathematics", "Computer Science"],
        "confidence": {"Mathematics": 1, "Computer Science": 4},
        "recent_questions": [],
    }
    plan = build_navigation_plan(snapshot, focus_subject="Computer Science")
    assert "Computer Science" in plan[0]["title"]
    assert "selected" in plan[0]["reason"].lower()


def test_empty_profile_recommends_profile_setup_without_predicting_results():
    snapshot = {
        "subjects": [],
        "confidence": {},
        "recent_questions": [],
    }
    plan = build_navigation_plan(snapshot)
    assert "profile" in plan[0]["title"].lower()
    assert "Add" in plan[0]["action"]
    assert all("grade" not in item["title"].lower() for item in plan)
