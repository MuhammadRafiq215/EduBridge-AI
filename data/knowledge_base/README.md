# EduBridge AI knowledge base

This folder stores short, reviewed, source-attributed knowledge records.

## Current starter coverage

The initial `documents.jsonl` contains seven reviewed official-source summaries:

- Cambridge IGCSE qualification overview and grade-threshold guidance
- Cambridge qualification recognition in Pakistan
- Pearson Edexcel International GCSE overview
- FBISE revised grading formula notification (with its separate 2026/2027 implementation dates)
- Türkiye Ministry of National Education upper-secondary assessment overview
- WAEC WASSCE Data Processing e-Learning resource page

This is a starter set, not comprehensive coverage of these boards or their subjects. It does not yet cover every syllabus, subject, exam series, national board or qualification.

## Add a record

Add one JSON object per line to `documents.jsonl`. Do not commit full copyrighted
syllabuses, paid textbooks, exam papers or other materials unless redistribution is
clearly permitted. Prefer short, carefully paraphrased facts and link to the official
source document.

Required fields:

- `source_id`: stable unique identifier, e.g. `CAMBRIDGE-IGCSE-GRADING-2026`
- `title`: exact title of the official source
- `issuer`: examination authority or government department
- `source_url`: official HTTPS source URL
- `qualification`: exact qualification or `General`
- `country`: country or `General`
- `board`: awarding body or `General`
- `topic`: concise topic label
- `content`: short factual summary in your own words
- `status`: `review_required`, `verified` or `archived`
- `reviewed_at`: ISO date of the human review
- `is_official`: boolean; only true for a source published by the responsible authority

A record is retrieved only when `status` is `verified` and `is_official` is true.
A record marked `review_required` is deliberately excluded from AI answers.

## Review checklist

1. Confirm that the URL belongs to the examination authority or responsible government body.
2. Check the qualification, country, awarding body, academic year and document version.
3. Record the publication/effective date when the source provides one.
4. Paraphrase only the facts needed; keep the source URL and a review date.
5. Have a second reviewer check high-impact facts such as grading, eligibility, assessment and progression rules.
6. Archive superseded records instead of silently overwriting historical rules.
