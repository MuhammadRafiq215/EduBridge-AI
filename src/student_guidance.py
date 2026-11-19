"""Student-facing guidance built from self-reported learner profiles.

This module deliberately produces descriptive study guidance, not admissions
probabilities, diagnoses, or predictions about individual academic outcomes.
"""
from __future__ import annotations

PATHWAYS = {
    "Engineering": {
        "description": "Explore engineering disciplines through mathematics, physics and problem-solving.",
        "focus": ["Mathematics", "Physics", "Chemistry", "Computing"],
        "projects": ["Build a simple bridge or structure model", "Measure and graph a real-world physical system", "Create a small Python calculation tool"],
        "degrees": ["Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Computer Engineering"],
    },
    "Computer Science & AI": {
        "description": "Build foundations in computing, logic, mathematics and practical software.",
        "focus": ["Mathematics", "Computer Science", "English", "Physics"],
        "projects": ["Create a small Python application", "Analyse a public dataset and explain its limits", "Build a simple website or automation"],
        "degrees": ["Computer Science", "Artificial Intelligence", "Data Science", "Software Engineering"],
    },
    "Medicine & Health Sciences": {
        "description": "Explore biology, chemistry, quantitative reasoning and evidence-based care.",
        "focus": ["Biology", "Chemistry", "Physics", "English"],
        "projects": ["Create a science concept explainer", "Compare public-health statistics from trusted sources", "Build a glossary of core biology terms"],
        "degrees": ["Medicine", "Dentistry", "Pharmacy", "Biomedical Sciences", "Nursing"],
    },
    "Economics & Business": {
        "description": "Develop quantitative reasoning, economics, communication and analytical skills.",
        "focus": ["Mathematics", "Economics", "Accounting", "English"],
        "projects": ["Analyse a public economic indicator", "Build a personal budget spreadsheet using fictional data", "Explain a market concept with a simple chart"],
        "degrees": ["Economics", "Finance", "Accounting", "Business Analytics", "Management"],
    },
    "Natural Sciences & Biotechnology": {
        "description": "Connect scientific reasoning with mathematics, laboratory concepts and computing.",
        "focus": ["Biology", "Chemistry", "Mathematics", "Physics"],
        "projects": ["Write a literature-based science explainer", "Visualise a public scientific dataset", "Document a safe, classroom-level observation"],
        "degrees": ["Biotechnology", "Biochemistry", "Chemistry", "Physics", "Environmental Science"],
    },
    "Social Sciences & Education": {
        "description": "Build research, communication, quantitative and critical-thinking skills.",
        "focus": ["English", "Mathematics", "Psychology", "Economics"],
        "projects": ["Review a public education dataset", "Create a short evidence-based explainer", "Compare two research articles and their methods"],
        "degrees": ["Psychology", "Education", "Sociology", "Political Science", "Public Policy"],
    },
    "Architecture & Design": {
        "description": "Combine visual communication, design thinking, mathematics and spatial reasoning.",
        "focus": ["Mathematics", "Art & Design", "Physics", "Computing"],
        "projects": ["Create a small design portfolio", "Sketch and annotate a user-centred space", "Build a simple 3D or digital design study"],
        "degrees": ["Architecture", "Industrial Design", "Urban Planning", "Interaction Design"],
    },
}

LEVELS = [
    "Middle school",
    "Matric / O Levels",
    "Intermediate / A Levels",
    "Undergraduate (BS)",
]

LEVEL_SUBJECTS = {
    "Middle school": ["Mathematics", "General Science", "English", "Computer Studies", "Social Studies", "Biology", "Chemistry", "Physics"],
    "Matric / O Levels": ["Mathematics", "Additional Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "English", "Economics", "Accounting", "Business Studies", "Urdu", "Pakistan Studies"],
    "Intermediate / A Levels": ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Accounting", "Business", "English", "Psychology"],
    "Undergraduate (BS)": ["Calculus", "Linear Algebra", "Statistics", "Programming", "Data Structures", "Algorithms", "Physics", "Chemistry", "Biology", "Microeconomics", "Macroeconomics", "Accounting", "Psychology", "Research Methods", "Academic Writing", "Engineering Mechanics"],
}


def build_learning_snapshot(profile: dict) -> dict:
    """Summarise self-rated subject confidence and suggest next learning steps."""
    pathway = profile.get("pathway", "Computer Science & AI")
    pathway_info = PATHWAYS.get(pathway, PATHWAYS["Computer Science & AI"])
    ratings = profile.get("confidence", {})
    valid = {str(subject): int(score) for subject, score in ratings.items() if score is not None}
    if not valid:
        raise ValueError("Add at least one subject confidence rating to build your snapshot.")
    average = sum(valid.values()) / len(valid)
    ordered = sorted(valid.items(), key=lambda item: (item[1], item[0]))
    focus = [subject for subject, score in ordered if score <= 3][:3]
    strengths = [subject for subject, score in sorted(valid.items(), key=lambda item: (-item[1], item[0])) if score >= 4][:3]
    pathway_matches = [subject for subject in pathway_info["focus"] if subject in valid]
    missing = [subject for subject in pathway_info["focus"] if subject not in valid]
    return {
        "pathway": pathway,
        "level": profile.get("level", "Not specified"),
        "subjects_rated": len(valid),
        "average_confidence": round(average, 2),
        "confidence_label": "Building foundations" if average < 2.5 else "Developing" if average < 3.8 else "Confident in self-review",
        "focus_subjects": focus,
        "strength_subjects": strengths,
        "pathway_subjects_reviewed": pathway_matches,
        "pathway_subjects_to_add": missing,
        "next_steps": [
            f"Set one small weekly goal for {subject}." for subject in focus
        ] or ["Choose one advanced topic in a strong subject and practise applying it."],
        "note": "This is a reflection based on your own ratings, not an objective grade, admissions assessment, or AI prediction.",
    }


def build_weekly_plan(profile: dict) -> list[dict]:
    """Allocate the learner's stated weekly study time across focus subjects."""
    snapshot = build_learning_snapshot(profile)
    hours = max(1, min(40, int(profile.get("weekly_hours", 5))))
    subjects = snapshot["focus_subjects"] or snapshot["pathway_subjects_reviewed"] or list(profile.get("confidence", {}))
    subjects = subjects[:3]
    if not subjects:
        raise ValueError("Choose subjects before generating a study plan.")
    allocations = [hours // len(subjects)] * len(subjects)
    for index in range(hours % len(subjects)):
        allocations[index] += 1
    return [
        {"subject": subject, "hours": allocation, "activity": "Review one concept, practise questions, then note what remains unclear."}
        for subject, allocation in zip(subjects, allocations)
    ]
