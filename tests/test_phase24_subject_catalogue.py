from src.ai_teacher_ui import _build_subject_options


def test_subject_options_include_large_catalogue_and_general_study():
    options = _build_subject_options([])
    assert "General study" in options
    assert "Mathematics" in options
    assert "Biology" in options
    assert "Computer Science" in options
    assert len(options) > 50
    assert options == sorted(options, key=str.casefold)


def test_subject_options_preserve_personal_subjects_and_remove_duplicates():
    options = _build_subject_options(["My own course", "Mathematics", "  ", 42])
    assert "My own course" in options
    assert options.count("Mathematics") == 1
    assert "General study" in options


def test_subject_options_ignore_malformed_profile_subjects():
    options = _build_subject_options(None)
    assert all(isinstance(item, str) and item.strip() for item in options)
