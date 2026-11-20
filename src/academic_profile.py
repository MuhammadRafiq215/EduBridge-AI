"""Transparent mark aggregation; board grades are never guessed."""
from __future__ import annotations

def calculate_academic_profile(subjects):
    if not isinstance(subjects, (list, tuple)) or not subjects:
        raise ValueError("Add at least one subject with marks.")
    clean, seen = [], set()
    for row in subjects:
        name = str(row.get("subject", "")).strip()
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            raise ValueError(f"Duplicate subject: {name}")
        seen.add(key)
        try:
            earned, maximum = float(row.get("marks_obtained")), float(row.get("maximum_marks"))
        except (TypeError, ValueError):
            raise ValueError(f"Enter numeric marks for {name}.")
        if maximum <= 0:
            raise ValueError(f"Maximum marks for {name} must be greater than zero.")
        if earned < 0 or earned > maximum:
            raise ValueError(f"Marks for {name} must be between 0 and {maximum:g}.")
        clean.append({"subject":name,"marks_obtained":earned,"maximum_marks":maximum,
                      "percentage":round(earned / maximum * 100, 2)})
    if not clean:
        raise ValueError("Add at least one valid subject.")
    total_earned, total_max = sum(x["marks_obtained"] for x in clean), sum(x["maximum_marks"] for x in clean)
    ranked = sorted(clean, key=lambda x:x["percentage"], reverse=True)
    return {
        "subject_count":len(clean),"total_marks_obtained":round(total_earned,2),
        "total_maximum_marks":round(total_max,2),"overall_percentage":round(total_earned / total_max * 100,2),
        "simple_average_subject_percentage":round(sum(x["percentage"] for x in clean)/len(clean),2),
        "strongest_subject":ranked[0]["subject"],"strongest_percentage":ranked[0]["percentage"],
        "improvement_subject":ranked[-1]["subject"],"improvement_percentage":ranked[-1]["percentage"],
        "subjects":clean,
        "interpretation":"Overall percentage is total marks obtained divided by total maximum marks. The simple subject average gives every subject equal weight and is shown separately.",
        "grade_note":"No letter grade, GPA, equivalency or admission prediction is assigned. Those require exact official grading or equivalency rules for the board, qualification, subject and examination session."
    }
