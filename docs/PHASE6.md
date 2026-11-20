# Phase 6 — Global Knowledge Base and Source-Aware Retrieval

## Objective
Build a traceable educational knowledge foundation across examination boards and qualifications. Prefer official awarding-body, examination-council and ministry sources; expose evidence; abstain when no reviewed source supports a result.

## First increment
- Versioned source registry and coverage tracker in data/knowledge/source_registry.json.
- TF-IDF retrieval with jurisdiction and qualification filters in src/knowledge_base.py.
- Labelled retrieval-development cases in data/knowledge/evaluation_cases.json.
- Unit tests for evidence eligibility, ranking, filtering, abstention and metrics.
- Streamlit Global Knowledge Hub page with source-linked search, coverage visualisation and retrieval evaluation.

## Evidence policy
A source marked verified_snippet means its official page was located and the short notes were reviewed. It does not mean the full qualification, current subject specification, examination structure or grading policy has been ingested. A discovery_pending pathway is visible in coverage but is not indexed as evidence.

Punjab, Sindh, KPK, Balochistan, AKU-EB, ÖSYM/YKS, AQA, OCR and BTEC remain research tasks in this increment. This is intentional: verify the official source before adding claims.

## Initial official source register
- Cambridge International awarding standards: https://www.cambridgeinternational.org/about-us/our-standards/awarding-standards/
- Pearson Edexcel International GCSE overview: https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/about-international-gcses.html
- FBISE syllabus and model papers: https://www.fbise.edu.pk/syllabus.php
- WAEC Nigeria WASSCE entry regulations: https://waecnigeria.org/node/102
- NECO SSCE Internal: https://neco.gov.ng/exams/ssce-internal
- NECO SSCE External: https://neco.gov.ng/exams/ssce-external
- IB Diploma Programme assessment: https://www.ibo.org/programmes/diploma-programme/assessment-and-exams/
- College Board AP courses and exams: https://apstudents.collegeboard.org/courses
- Türkiye MEB FAQ: https://www.meb.gov.tr/sss.php

The registry records each note's scope and limitations. Session-specific dates, subject offerings, exam modes and thresholds must be checked against the current official guide before advice is given.

## Retrieval design
The first release uses scikit-learn TfidfVectorizer with unigrams and bigrams and cosine similarity. Only reviewed source records are indexed. Each result carries its title, publisher, jurisdiction, qualification, reviewed notes, limitations and original official URL.

This is a lexical-semantic baseline, not a dense-vector embedding model. Source ingestion, retrieval and answer generation are separated so later embeddings or rerankers can be evaluated without losing provenance.

## Evaluation
The development set labels each query with expected source IDs.
- Recall@k: fraction of questions for which at least one expected source appears in the top k.
- MRR@k: mean reciprocal rank of the first expected source in the top k.

The current set is small and curated. It is a regression harness, not a representative benchmark and not a measure of answer factuality. Add hard negatives, paraphrases, cross-board confusions, subject-specific queries, expert-reviewed answer keys and a held-out test set before drawing quality conclusions.

## Run and test
Run python -m unittest discover -s tests -v, then streamlit run app.py. The Global Knowledge Hub is available through Streamlit multipage navigation.

## Next increments
1. Verify official source discovery for each pending national system and awarding body.
2. Index current subject specifications and assessment guides where permitted; preserve title, version, effective date, page/section and URL.
3. Structure subject content, paper/component structure, assessment weighting, grading and exam-session rules.
4. Add source freshness checks and version-aware updates.
5. Build expert-reviewed question/answer pairs and a held-out evaluation set.
6. Compare TF-IDF with dense embeddings and hybrid retrieval; report Recall@k, MRR, citation correctness and answer faithfulness.
7. Add qualification-aware answer synthesis only after retrieval quality and citation behaviour are demonstrated.

## Responsible use and copyright
Do not present overview pages as subject specifications or invent universal grade boundaries/equivalencies. Do not copy full copyrighted syllabuses, paid resources or examination papers. Store metadata, concise factual notes, permitted excerpts and links. Keep citations visible in the UI.
