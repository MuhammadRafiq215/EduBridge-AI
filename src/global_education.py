"""Global education-system, qualification and subject catalogues.

Country coverage is generated from ISO 3166 country data when pycountry is
available. Qualification lists are starter references, not exhaustive legal
registries; learners can always enter a custom curriculum or awarding body.
"""
from __future__ import annotations

try:
    import pycountry
except ImportError:  # pragma: no cover - keeps local fallback usable
    pycountry = None

INTERNATIONAL_QUALIFICATIONS = [
    "Cambridge International (IGCSE / O Level / AS & A Level)",
    "Pearson Edexcel (International GCSE / International A Level)",
    "International Baccalaureate (PYP / MYP / DP / CP)",
    "Advanced Placement (AP)",
    "AQA",
    "OCR",
    "WJEC / Eduqas",
    "CCEA",
    "BTEC",
    "Other international qualification",
]

NATIONAL_SYSTEMS = {
    "Pakistan": ["Federal Board (FBISE)", "Punjab Boards (BISE)", "Sindh Boards (BISE)", "KPK Boards (BISE)", "Balochistan Board", "Aga Khan University Examination Board (AKU-EB)", "Technical / vocational board"],
    "India": ["CBSE", "CISCE (ICSE / ISC)", "State Board", "NIOS", "Other national / state board"],
    "United States": ["State High School Diploma", "GED", "Other state / local programme"],
    "United Kingdom": ["England national curriculum", "Scotland Curriculum for Excellence", "Wales Curriculum for Wales", "Northern Ireland Curriculum"],
    "Canada": ["Provincial / territorial curriculum", "Quebec DES / CEGEP", "Other provincial programme"],
    "Australia": ["Australian Curriculum / state or territory certificate", "ATAR pathway", "VET / TAFE"],
    "New Zealand": ["NCEA", "Cambridge pathway", "Other NZ qualification"],
    "Bangladesh": ["Dhaka Education Board", "Chattogram Education Board", "Rajshahi Education Board", "Other education board"],
    "Nepal": ["National Examination Board (NEB)", "CTEVT", "Other national programme"],
    "Sri Lanka": ["GCE Ordinary Level", "GCE Advanced Level", "Other national programme"],
    "Nigeria": ["WAEC", "NECO", "NABTEB", "JAMB", "Other national programme"],
    "Ghana": ["WAEC", "WASSCE", "TVET", "Other national programme"],
    "Kenya": ["CBC", "KCSE", "TVET", "Other national programme"],
    "South Africa": ["National Senior Certificate (NSC)", "IEB", "TVET", "Other national programme"],
    "United Arab Emirates": ["UAE Ministry of Education curriculum", "Emirates Standardized Test pathway", "Other UAE programme"],
    "Saudi Arabia": ["Saudi national curriculum", "TVTC / technical pathway", "Other national programme"],
    "Türkiye": ["MEB national curriculum", "Anatolian / Science High School pathway", "Other national programme"],
    "Malaysia": ["KSSM / SPM", "STPM", "Matriculation", "UEC", "Other national programme"],
    "Singapore": ["Singapore-Cambridge GCE", "Polytechnic", "ITE", "Other national programme"],
    "China": ["National College Entrance Examination (Gaokao)", "Senior High School Academic Proficiency Test", "Other national programme"],
    "Japan": ["MEXT national curriculum", "Upper Secondary School Certificate", "Other national programme"],
    "South Korea": ["National Curriculum", "CSAT / Suneung pathway", "Other national programme"],
    "Philippines": ["DepEd K–12", "Senior High School track", "TESDA", "Other national programme"],
    "Indonesia": ["Kurikulum Merdeka", "National curriculum pathway", "Other national programme"],
    "France": ["French national curriculum", "Baccalauréat général / technologique / professionnel"],
    "Germany": ["Abitur", "Fachhochschulreife", "State / Länder curriculum"],
}

SUBJECT_GROUPS = {
    "Mathematics & quantitative": ["Mathematics", "Additional Mathematics", "Further Mathematics", "Pure Mathematics", "Statistics", "Probability", "Calculus", "Linear Algebra", "Discrete Mathematics", "Applied Mathematics"],
    "Natural sciences": ["General Science", "Biology", "Human Biology", "Chemistry", "Physics", "Environmental Science", "Earth Science", "Astronomy", "Geology", "Marine Science"],
    "Computing & technology": ["Computer Science", "Computer Studies", "Information Technology", "Programming", "Data Structures", "Algorithms", "Artificial Intelligence", "Data Science", "Cybersecurity", "Web Development", "Database Systems", "Robotics", "Digital Literacy"],
    "Languages & communication": ["English", "Academic Writing", "Literature", "Urdu", "Arabic", "French", "German", "Spanish", "Chinese", "Japanese", "Korean", "Turkish", "Other language"],
    "Humanities & social sciences": ["History", "Geography", "Social Studies", "Civics", "Political Science", "Sociology", "Psychology", "Philosophy", "Religious Studies", "Global Perspectives", "Anthropology"],
    "Business, economics & law": ["Economics", "Accounting", "Business Studies", "Business Management", "Finance", "Marketing", "Entrepreneurship", "Commerce", "Law", "Business Analytics"],
    "Creative arts & media": ["Art & Design", "Fine Art", "Music", "Drama", "Theatre", "Media Studies", "Film Studies", "Graphic Design", "Photography", "Design Technology"],
    "Health, sport & wellbeing": ["Physical Education", "Health Science", "Nutrition", "Sports Science", "Public Health", "Nursing Studies"],
    "Engineering & applied studies": ["Engineering", "Engineering Mechanics", "Electronics", "Mechanics", "Design & Technology", "Agriculture", "Food Science", "Hospitality & Tourism"],
    "University & research": ["Research Methods", "Academic Skills", "Professional Communication", "Project Management", "Laboratory Skills"],
}

FIELDS_OF_INTEREST = [
    "Computer Science & Software", "Artificial Intelligence & Data Science",
    "Engineering & Technology", "Medicine & Health Sciences",
    "Biological & Life Sciences", "Physical & Natural Sciences",
    "Mathematics & Statistics", "Business, Finance & Economics",
    "Law & International Relations", "Education & Teaching",
    "Social Sciences & Psychology", "Arts, Design & Architecture",
    "Media, Communication & Journalism", "Agriculture & Food Systems",
    "Environment & Sustainability", "Hospitality & Tourism",
    "Skilled Trades & Vocational Careers", "Undecided / Exploring",
]

def get_countries() -> list[str]:
    """Return a broad ISO country list, with a safe fallback."""
    if pycountry is not None:
        names = sorted({country.name for country in pycountry.countries})
        return names + ["Other / not listed"]
    return sorted({
        "Australia", "Bangladesh", "Brazil", "Canada", "China", "France",
        "Germany", "Ghana", "India", "Indonesia", "Japan", "Kenya",
        "Malaysia", "Nepal", "New Zealand", "Nigeria", "Pakistan",
        "Philippines", "Saudi Arabia", "Singapore", "South Africa",
        "South Korea", "Sri Lanka", "Türkiye", "United Arab Emirates",
        "United Kingdom", "United States", "Other / not listed",
    })

def get_qualification_options(country: str) -> list[str]:
    """Combine global qualifications with country-specific pathways."""
    national = NATIONAL_SYSTEMS.get(country, ["National curriculum / government qualification"])
    return ["National curriculum / qualification"] + national + INTERNATIONAL_QUALIFICATIONS + [
        "University / higher education", "Technical / vocational qualification",
        "Other / not sure",
    ]

def get_subject_options() -> list[str]:
    """Flatten the broad subject catalogue while preserving readable labels."""
    return [subject for subjects in SUBJECT_GROUPS.values() for subject in subjects]
