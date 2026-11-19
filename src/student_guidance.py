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
        "resources": [["Khan Academy — Maths & Physics","https://www.khanacademy.org/"],["MIT OpenCourseWare","https://ocw.mit.edu/"]],
    },
    "Computer Science & AI": {
        "description": "Build foundations in computing, logic, mathematics and practical software.",
        "focus": ["Mathematics", "Computer Science", "English", "Physics"],
        "projects": ["Create a small Python application", "Analyse a public dataset and explain its limits", "Build a simple website or automation"],
        "degrees": ["Computer Science", "Artificial Intelligence", "Data Science", "Software Engineering"],
        "resources": [["CS50 — Introduction to Computer Science","https://cs50.harvard.edu/x/"],["freeCodeCamp","https://www.freecodecamp.org/"],["Python Tutorial","https://docs.python.org/3/tutorial/"]],
    },
    "Medicine & Health Sciences": {
        "description": "Explore biology, chemistry, quantitative reasoning and evidence-based care.",
        "focus": ["Biology", "Chemistry", "Physics", "English"],
        "projects": ["Create a science concept explainer", "Compare public-health statistics from trusted sources", "Build a glossary of core biology terms"],
        "degrees": ["Medicine", "Dentistry", "Pharmacy", "Biomedical Sciences", "Nursing"],
        "resources": [["Khan Academy — Health & Medicine","https://www.khanacademy.org/science/health-and-medicine"],["OpenStax — Anatomy & Physiology","https://openstax.org/details/books/anatomy-and-physiology-2e"]],
    },
    "Economics & Business": {
        "description": "Develop quantitative reasoning, economics, communication and analytical skills.",
        "focus": ["Mathematics", "Economics", "Accounting", "English"],
        "projects": ["Analyse a public economic indicator", "Build a personal budget spreadsheet using fictional data", "Explain a market concept with a simple chart"],
        "degrees": ["Economics", "Finance", "Accounting", "Business Analytics", "Management"],
        "resources": [["CORE Econ — The Economy","https://www.core-econ.org/the-economy/"],["Khan Academy — Economics","https://www.khanacademy.org/economics-finance-domain"]],
    },
    "Natural Sciences & Biotechnology": {
        "description": "Connect scientific reasoning with mathematics, laboratory concepts and computing.",
        "focus": ["Biology", "Chemistry", "Mathematics", "Physics"],
        "projects": ["Write a literature-based science explainer", "Visualise a public scientific dataset", "Document a safe, classroom-level observation"],
        "degrees": ["Biotechnology", "Biochemistry", "Chemistry", "Physics", "Environmental Science"],
        "resources": [["OpenStax — Free textbooks","https://openstax.org/subjects/science"],["Khan Academy — Science","https://www.khanacademy.org/science"]],
    },
    "Social Sciences & Education": {
        "description": "Build research, communication, quantitative and critical-thinking skills.",
        "focus": ["English", "Mathematics", "Psychology", "Economics"],
        "projects": ["Review a public education dataset", "Create a short evidence-based explainer", "Compare two research articles and their methods"],
        "degrees": ["Psychology", "Education", "Sociology", "Political Science", "Public Policy"],
        "resources": [["OpenLearn — Free courses","https://www.open.edu/openlearn/"],["MIT OpenCourseWare","https://ocw.mit.edu/"]],
    },
    "Architecture & Design": {
        "description": "Combine visual communication, design thinking, mathematics and spatial reasoning.",
        "focus": ["Mathematics", "Art & Design", "Physics", "Computing"],
        "projects": ["Create a small design portfolio", "Sketch and annotate a user-centred space", "Build a simple 3D or digital design study"],
        "degrees": ["Architecture", "Industrial Design", "Urban Planning", "Interaction Design"],
        "resources": [["MIT OpenCourseWare — Architecture","https://ocw.mit.edu/search/?d=Architecture"],["Khan Academy — Geometry","https://www.khanacademy.org/math/geometry"]],
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

def build_personalised_recommendations(profile: dict) -> dict:
    """Create transparent, profile-based learning priorities and explain their rationale.

    This is a deterministic recommendation system, not a trained predictive model.
    It uses only the learner's self-reported confidence, selected pathway and subjects.
    """
    snapshot = build_learning_snapshot(profile)
    pathway_info = PATHWAYS.get(snapshot["pathway"], PATHWAYS["Computer Science & AI"])
    ratings = {
        str(subject): max(1, min(5, int(score)))
        for subject, score in profile.get("confidence", {}).items()
        if score is not None
    }
    pathway_focus = pathway_info["focus"]
    ranked = []
    for subject, confidence in ratings.items():
        pathway_match = subject in pathway_focus
        # Lower confidence increases support priority; pathway relevance breaks ties.
        score = (6 - confidence) * 2 + (1.5 if pathway_match else 0)
        if confidence <= 2:
            priority = "High support"
            action = f"Review one core {subject} concept, then complete a short set of practice questions and note what is still unclear."
        elif confidence == 3:
            priority = "Build consistency"
            action = f"Practise {subject} in two short sessions: one for concept review and one for applying it to questions or a small task."
        else:
            priority = "Maintain and extend"
            action = f"Keep {subject} active with a mixed practice task or a small project that connects it to your chosen field."
        reasons = [f"your confidence rating is {confidence}/5"]
        if pathway_match:
            reasons.append(f"{subject} is one of the preparation themes listed for {snapshot['pathway']}")
        ranked.append({
            "subject": subject,
            "confidence": confidence,
            "priority": priority,
            "score": round(score, 1),
            "reason": "; ".join(reasons),
            "action": action,
        })
    ranked.sort(key=lambda item: (-item["score"], item["subject"].casefold()))
    gaps = [subject for subject in pathway_focus if subject not in ratings]
    weekly_hours = max(1, min(40, int(profile.get("weekly_hours", 5))))
    return {
        "pathway": snapshot["pathway"],
        "recommendations": ranked[:3],
        "pathway_gaps": gaps,
        "weekly_hours": weekly_hours,
        "method": "Transparent profile-based ranking",
        "note": "Recommendations use your self-reported confidence and selected pathway. They are study-planning suggestions, not grades, admissions predictions or a trained ML model.",
    }

