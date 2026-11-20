# Phase 6 — Global Knowledge and Academic Intelligence

## This increment
- Expanded the source registry with Pakistan provincial and board resources, Cambridge subject directories, Pearson subject availability, Ofqual, Russia FIPI, US AP, India CBSE and Türkiye MEB.
- Added broad subject discovery data in data/knowledge/subject_catalog.json.
- Added transparent mark aggregation in src/academic_profile.py and the Academic Profile Analyzer Streamlit page.
- Fixed TF-IDF tokenisation so the reviewed-source index builds.
- Added regression tests for retrieval and academic mark calculations.

## Evidence labels
- verified_snippet: official overview/page reviewed; concise factual notes only.
- catalogue_verified: official subject catalogue reviewed; not a complete specification.
- historical_reference: official historical document useful for discovery, not current rules.
- discovery_pending: not yet verified.
- specification_verified: reserve for a specific current subject specification actually reviewed.

## Pakistan-first source set
- FBISE: https://www.fbise.edu.pk/syllabus.php
- Punjab PECTAA: https://pectaa.edu.pk/curriculum-compliance/
- BISE Lahore: https://www.biselahore.com/notifications
- BISE Peshawar: https://www.bisep.edu.pk/page-10098.html
- BISE Malakand: https://bisemalakand.edu.pk/downloadforms?cat_id=9
- Balochistan curriculum: https://sed.gob.pk/curriculum.html
- BSEK 2025 optional subject notice: https://bsek.edu.pk/uploads/Reduced%20Syllabus%20of%20some%20optional%20subjects%20corrected%20by%20%20General%20Group%20IX-X%202025.pdf
- AKU-EB scheme (historical/reference): https://examinationboard.aku.edu/learning-materials/documents/hssc%20-%20scheme%20of%20studies.pdf
- BIEK reduced syllabus 2020–21 (historical only): https://biek.edu.pk/Notifications/2020/Reduce%20Syllabus%20XI%20-XII.pdf

## International catalogues
- Cambridge IGCSE: https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-upper-secondary/cambridge-igcse/subjects/
- Cambridge AS/A Level: https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-advanced/cambridge-international-as-and-a-levels/subjects/
- Pearson International GCSE: https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses.html
- College Board AP: https://apstudents.collegeboard.org/courses
- Ofqual 2026: https://www.gov.uk/government/publications/ofqual-guide-for-schools-and-colleges-2026
- Russia FIPI: https://fipi.ru/ege and https://fipi.ru/ege/demoversii-specifikacii-kodifikatory
- Türkiye MEB: https://tymm.meb.gov.tr/ogretim-programlari/matematik-dersi
- India CBSE: https://www.cbse.gov.in/cbsenew/Curriculum.html

## Academic profile calculations
1. Overall weighted percentage = total marks obtained / total maximum marks × 100.
2. Equal-weight subject average = arithmetic mean of subject percentages.
3. Subject-wise percentages and highest/lowest entered subjects.

The analyzer validates duplicates, missing numeric values, negative marks and marks exceeding maximum. It does not infer grades, GPA, equivalencies, admission eligibility or predicted results. Conversion requires exact official grading rules for board, qualification, subject and session. The page does not request student identity details.

## Evaluation and next steps
The curated development set measures source retrieval only. It does not establish answer factuality. Next: current full subject catalogues for every Pakistan board; current Cambridge and Pearson subject specifications and component codes; country-specific WAEC/NECO catalogues; ÖSYM YKS; US state requirements; AQA/OCR/WJEC/CCEA; Russia OGE/EGE; then source-version-aware ingestion and expert-reviewed held-out evaluation.
