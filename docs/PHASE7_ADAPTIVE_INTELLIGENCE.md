# Phase 7 — Adaptive Student Intelligence

## What this phase adds

- Topic-level progress entries with subject, topic, study date, self-reported confidence, practice attempts and correct answers.
- A transparent progress indicator: 60% practice accuracy + 40% self-reflected confidence.
- A provisional label until at least five practice attempts are recorded.
- Adaptive next-step suggestions based on the latest entry for each subject/topic.
- Optional account persistence for topic progress through the existing learner profile row.
- Optional cross-session AI Teacher chat history, off by default, with per-user row-level security and a delete control.
- A larger official-source registry with version-specific Cambridge and Pearson Computer Science specifications and additional FBISE and IB official records.

## Topic progress methodology

The progress index is a descriptive planning signal, not a grade, prediction, diagnosis or validated mastery score. It uses only student-entered practice counts and confidence. The latest dated record for each subject/topic is shown. If fewer than five practice questions are recorded, the UI labels the result provisional and recommends collecting more practice evidence.

The system does not infer a learner's ability from chat messages, identity, school, location or demographic attributes. It does not compare learners or rank them.

## Persistence and privacy

### Topic progress

- Without sign-in, newly entered topic progress stays in the current Streamlit browser session.
- With sign-in, the learner can explicitly choose to save topic records to their own existing profile.
- Profile data remains protected by the existing `student_profiles` row-level security policies.
- The app does not save topic progress to a shared/public table.

### AI Teacher chat history

- Permanent chat saving is off by default.
- It requires an authenticated account and a separate opt-in checkbox.
- Only text messages and assistant answers are stored; uploaded screenshots are not saved.
- The database stores at most the latest 100 user/assistant messages, with a 10,000-character limit per message; older messages are trimmed as new ones are saved.
- Row-level security restricts read, insert, update and delete to the matching authenticated user.
- The AI Teacher includes a delete-saved-history action.
- Apply `supabase/chat_history_schema.sql` only after checking the account provider's eligibility, privacy and data-handling terms. The migration has not been run automatically.
- No service-role key is used or required by the app.

A database migration is not the same as an active database. Persistent history will work only after the user has an eligible, configured Supabase project, has applied the migration, and has signed in. Until then, chat remains temporary and the UI must not claim otherwise.

## AI provider status

The provider adapter from Phase 6.4 remains in place. It is not activated by this phase. No API key or provider account is created or embedded in the repository. Before configuring a live provider, verify age eligibility, account terms, data retention, privacy and pricing. Do not bypass those requirements.

## Knowledge registry expansion

Added and reviewed these official records:

| Record | Scope | Evidence status |
|---|---|---|
| Cambridge 9618 syllabus 2027–2029 | Exact AS & A Level Computer Science syllabus and version | `specification_verified` |
| Pearson Edexcel IAL Computer Science Issue 1 (March 2026) | New XCP01/YCP01 qualification and unit structure | `specification_verified` |
| FBISE revised Scheme of Studies 2024 notification (16 Nov 2026) | SSC bilingual-paper policy from First Annual 2027 | `verified_snippet` |
| IB Diploma Programme assessment overview | Programme-level assessment principles | `verified_snippet` |

The new Cambridge and Pearson records are specific to their stated qualification and versions. FBISE and IB entries remain snippets, not complete subject specifications. The registry does not claim all qualifications or subjects are covered.

## Validation

- Unit tests cover topic input validation, provisional evidence, latest-record selection, adaptive next actions, chat-history allow-listing, and version-specific source retrieval.
- GitHub Actions runs compilation and the repository's unit tests.
- A green CI run confirms those checks, not a complete live-provider or remote-database integration test.
