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
    """Allocate weekly study time using self-rated confidence and pathway relevance.

    Lower confidence receives a larger share. A subject relevant to the selected
    pathway receives a modest additional weight. This is transparent planning
    logic, not a trained model or a measure of ability.
    """
    snapshot = build_learning_snapshot(profile)
    hours = max(1, min(40, int(profile.get("weekly_hours", 5))))
    subjects = snapshot["focus_subjects"] or snapshot["pathway_subjects_reviewed"] or list(profile.get("confidence", {}))
    subjects = subjects[:min(3, hours)]
    if not subjects:
        raise ValueError("Choose subjects before generating a study plan.")

    pathway_focus = PATHWAYS.get(snapshot["pathway"], PATHWAYS["Computer Science & AI"])["focus"]
    ratings = profile.get("confidence", {})
    weights = []
    for subject in subjects:
        confidence = max(1, min(5, int(ratings.get(subject, 3))))
        pathway_bonus = 1.25 if subject in pathway_focus else 0
        weights.append((6 - confidence) + pathway_bonus)

    # Give every selected subject one hour, then distribute the remaining
    # hours proportionally using the largest-remainder method.
    allocations = [1] * len(subjects)
    remaining = hours - len(subjects)
    if remaining:
        total_weight = sum(weights)
        exact = [remaining * weight / total_weight for weight in weights]
        whole = [int(value) for value in exact]
        allocations = [base + extra for base, extra in zip(allocations, whole)]
        leftover = remaining - sum(whole)
        # Resolve leftover hours in priority order so a lower-confidence
        # subject is not disadvantaged by a fractional-rounding tie.
        order = sorted(range(len(subjects)), key=lambda index: (-weights[index], subjects[index].casefold()))
        for index in order[:leftover]:
            allocations[index] += 1

    rows = []
    for subject, allocation in zip(subjects, allocations):
        confidence = max(1, min(5, int(ratings.get(subject, 3))))
        if confidence <= 2:
            activity = f"Build the foundations in {subject}: review one core idea, work through a few guided examples and write down one question to revisit."
        elif confidence == 3:
            activity = f"Strengthen {subject}: review a concept, practise applying it and check your understanding."
        else:
            activity = f"Maintain {subject}: use mixed practice or a small project to apply what you already know."
        rows.append({"subject": subject, "hours": allocation, "activity": activity,
                     "confidence": confidence,
                     "allocation_reason": "More time is assigned to lower-confidence subjects; pathway relevance is a small tie-breaker."})
    return rows

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



# Expanded career discovery catalogue, aligned to the modern Career Clusters framework.
# Preparation themes are exploratory examples; exact prerequisites vary by country,
# institution and degree programme.
PATHWAYS.update({
    "Agriculture & Food Systems": {
        "description": "Explore food systems, sustainable agriculture, animal science and the technologies that support communities.",
        "focus": ["Biology", "Chemistry", "Environmental Science", "Mathematics", "Geography", "Computing"],
        "projects": ["Map local food supply chains using public information", "Analyse a public agriculture or climate dataset", "Design a simple water-use awareness dashboard"],
        "degrees": ["Agricultural Science", "Food Science & Technology", "Animal Science", "Agribusiness", "Horticulture", "Food Engineering"],
        "resources": [["FAO — Education and learning", "https://www.fao.org/"], ["OpenStax Biology", "https://openstax.org/subjects/science"]],
    },
    "Energy & Environmental Science": {
        "description": "Investigate energy systems, climate, conservation and practical approaches to environmental challenges.",
        "focus": ["Physics", "Chemistry", "Mathematics", "Biology", "Geography", "Computing"],
        "projects": ["Visualise a public climate dataset", "Compare solar-energy output scenarios with fictional data", "Create a local biodiversity information guide"],
        "degrees": ["Environmental Science", "Renewable Energy Engineering", "Climate Science", "Geology", "Environmental Management", "Sustainable Development"],
        "resources": [["NASA Climate", "https://climate.nasa.gov/"], ["Our World in Data — Environment", "https://ourworldindata.org/environment"]],
    },
    "Finance & Accounting": {
        "description": "Understand how organisations manage money, measure performance and make evidence-based financial decisions.",
        "focus": ["Mathematics", "Statistics", "Accounting", "Economics", "Business Studies", "Computing"],
        "projects": ["Build a fictional monthly budget spreadsheet", "Create a simple financial-ratio explainer using sample data", "Visualise a public economic indicator"],
        "degrees": ["Accounting", "Finance", "Actuarial Science", "Banking", "Financial Economics", "Business Analytics"],
        "resources": [["CORE Econ", "https://www.core-econ.org/"], ["Khan Academy — Finance", "https://www.khanacademy.org/economics-finance-domain"]],
    },
    "Law, Policy & International Relations": {
        "description": "Explore legal systems, public policy, diplomacy, governance and the careful use of evidence.",
        "focus": ["English", "History", "Civics", "Economics", "Politics", "Research Methods"],
        "projects": ["Compare public policy summaries from two official sources", "Create a plain-language guide to a public institution", "Write an evidence-based debate brief"],
        "degrees": ["Law (LLB)", "Political Science", "International Relations", "Public Policy", "Governance", "Criminology"],
        "resources": [["United Nations — Learning", "https://www.un.org/en/academic-impact"], ["OpenLearn", "https://www.open.edu/openlearn/"]],
    },
    "Media, Communication & Journalism": {
        "description": "Combine storytelling, research, visual communication and responsible reporting across digital and traditional media.",
        "focus": ["English", "Media Studies", "Art & Design", "Computing", "History", "Research Methods"],
        "projects": ["Produce a short fact-checked explainer", "Create an accessible infographic from public data", "Compare how two outlets frame the same public event"],
        "degrees": ["Journalism", "Mass Communication", "Media Studies", "Digital Media", "Film & Television", "Public Relations"],
        "resources": [["BBC Academy", "https://www.bbc.co.uk/academy"], ["Adobe Education Exchange", "https://edex.adobe.com/"]],
    },
    "Hospitality, Events & Tourism": {
        "description": "Explore visitor experiences, event planning, hospitality operations and sustainable tourism.",
        "focus": ["English", "Business Studies", "Geography", "Mathematics", "Communication", "Digital Skills"],
        "projects": ["Design a sample visitor guide for a local heritage site", "Create a fictional event budget", "Map an accessible one-day cultural itinerary"],
        "degrees": ["Hospitality Management", "Tourism Management", "Event Management", "Hotel Management", "Culinary Arts", "Travel Operations"],
        "resources": [["UN Tourism", "https://www.unwto.org/"], ["OpenLearn", "https://www.open.edu/openlearn/"]],
    },
    "Manufacturing, Robotics & Automation": {
        "description": "Discover how products are designed, built, tested and improved using engineering, computing and automation.",
        "focus": ["Mathematics", "Physics", "Chemistry", "Computer Science", "Design Technology", "Engineering"],
        "projects": ["Model a simple production workflow", "Build a safe software simulation of a sorting system", "Analyse quality-control sample data"],
        "degrees": ["Mechatronics Engineering", "Robotics Engineering", "Industrial Engineering", "Manufacturing Engineering", "Materials Science", "Automation"],
        "resources": [["MIT OpenCourseWare", "https://ocw.mit.edu/"], ["FIRST — Robotics", "https://www.firstinspires.org/"]],
    },
    "Cybersecurity & Networks": {
        "description": "Learn how digital systems communicate and how organisations protect information, privacy and services.",
        "focus": ["Computer Science", "Mathematics", "Physics", "Networking", "English", "Digital Ethics"],
        "projects": ["Draw a home-network concept map", "Build a password-strength education demo without collecting passwords", "Create a cyber-safety awareness guide"],
        "degrees": ["Cybersecurity", "Computer Networks", "Information Security", "Computer Science", "Digital Forensics", "Information Systems"],
        "resources": [["Cisco Networking Academy", "https://www.netacad.com/"], ["NIST Cybersecurity Framework", "https://www.nist.gov/cyberframework"]],
    },
    "Transportation & Logistics": {
        "description": "Study how people, goods and information move through transport systems and supply networks.",
        "focus": ["Mathematics", "Physics", "Geography", "Economics", "Computing", "Business Studies"],
        "projects": ["Map a fictional delivery route and compare travel times", "Visualise public transport data", "Draw a supply-chain process map"],
        "degrees": ["Logistics & Supply Chain Management", "Transport Planning", "Aerospace Engineering", "Aviation Management", "Marine Engineering", "Operations Research"],
        "resources": [["World Bank Transport", "https://www.worldbank.org/en/topic/transport"], ["Our World in Data", "https://ourworldindata.org/"]],
    },
    "Education & Learning Sciences": {
        "description": "Explore teaching, educational technology, learning research and ways to make knowledge accessible.",
        "focus": ["English", "Psychology", "Mathematics", "Computer Science", "Biology", "Research Methods"],
        "projects": ["Create a short interactive lesson", "Analyse an open education dataset", "Design a revision planner for a chosen topic"],
        "degrees": ["Education", "Educational Psychology", "Learning Sciences", "Special Education", "Educational Technology", "Teacher Education"],
        "resources": [["UNESCO Education", "https://www.unesco.org/en/education"], ["OpenLearn", "https://www.open.edu/openlearn/"]],
    },
    "Sports Science & Human Performance": {
        "description": "Investigate movement, exercise science, sports data and wellbeing through evidence-based study.",
        "focus": ["Biology", "Physics", "Mathematics", "Psychology", "Statistics", "Health Science"],
        "projects": ["Visualise a public sports dataset", "Create a sports-science concept explainer", "Compare fictional training-session data responsibly"],
        "degrees": ["Sports Science", "Exercise Physiology", "Kinesiology", "Sports Psychology", "Physical Education", "Sports Analytics"],
        "resources": [["OpenStax — Biology", "https://openstax.org/subjects/science"], ["Khan Academy", "https://www.khanacademy.org/"]],
    },
    "Public Service & Community Development": {
        "description": "Explore public institutions, community programmes, emergency planning and evidence-led services.",
        "focus": ["English", "Civics", "Geography", "Economics", "Statistics", "Research Methods"],
        "projects": ["Map publicly listed community services", "Summarise a public development indicator", "Create a community information resource"],
        "degrees": ["Public Administration", "Development Studies", "Social Work", "Public Policy", "Disaster Management", "Urban Studies"],
        "resources": [["UNDP", "https://www.undp.org/"], ["World Bank Data", "https://data.worldbank.org/"]],
    },
    "Veterinary & Animal Sciences": {
        "description": "Learn about animal biology, health, welfare and the science of animal populations and ecosystems.",
        "focus": ["Biology", "Chemistry", "Mathematics", "Environmental Science", "English"],
        "projects": ["Create an animal-biology learning guide", "Visualise a public biodiversity dataset", "Compare animal-welfare guidance from official organisations"],
        "degrees": ["Veterinary Medicine", "Animal Science", "Zoology", "Wildlife Biology", "Animal Nutrition", "Veterinary Public Health"],
        "resources": [["FAO", "https://www.fao.org/"], ["OpenStax Biology", "https://openstax.org/subjects/science"]],
    },
})


def search_pathways(query: str = "", subjects: list[str] | None = None) -> list[str]:
    """Return career sectors matching a learner's search text and chosen subjects."""
    term = (query or "").strip().casefold()
    chosen = {item.casefold() for item in (subjects or []) if isinstance(item, str)}
    matches = []
    for name, details in PATHWAYS.items():
        searchable = " ".join([
            name, details.get("description", ""),
            " ".join(details.get("focus", [])),
            " ".join(details.get("degrees", [])),
            " ".join(details.get("projects", [])),
        ]).casefold()
        text_match = not term or term in searchable
        subject_match = not chosen or bool(chosen.intersection(
            {item.casefold() for item in details.get("focus", [])}
        ))
        if text_match and subject_match:
            matches.append(name)
    return matches
