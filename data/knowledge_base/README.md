# EduBridge AI knowledge base

This folder is reserved for small, reviewed, source-attributed knowledge records.

## Add a record

Create `documents.jsonl` with one JSON object per line. Do not commit full copyrighted
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

The repository currently contains the retrieval engine but no verified exam-board records.
Do not describe any board's rules as indexed until approved records have been added.
