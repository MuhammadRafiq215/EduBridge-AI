# Specification Engine, AI Teacher and Student Navigator

## Architecture

The existing `src/knowledge_base.py` source registry and TF-IDF retrieval engine
remain the foundation. This phase adds a specification-aware adapter and a Student
Navigator on top of that foundation; it does not replace the existing registry,
coverage metadata, or retrieval evaluation set.

~~~text
Learner-approved profile + current browser-session chat
                       |
                       v
               Student Navigator
                       |
             focus / qualification /
              subject / year / series
                       |
                       v
        Specification-aware retrieval
                       |
          reviewed source registry
          + subject catalogue evidence
                       |
                       v
                  AI Teacher
                       |
           explanation + source IDs
~~~

## Evidence rules

- `specification_verified` means the exact official subject specification was
  reviewed for the stated qualification and version.
- `verified_snippet` is a short reviewed official-source summary, not a complete
  qualification specification.
- `catalogue_verified` confirms subject catalogue discovery only; it does not prove
  that the complete syllabus, paper structure or grading rules have been ingested.
- `historical_reference` is useful for context but must not be presented as current.
- `discovery_pending` means the official source has not yet been reviewed.

The Specification Engine passes these labels, source URLs, reviewed notes and
limitations to the tutor. It must not infer subject-specific paper structures,
grade thresholds, equivalencies or current-year rules from general landing pages.
For marks-to-grade questions, the exact board, qualification, subject and exam
session must match an official grading table.

## Student Navigator

The Navigator uses explicit profile fields: country, level, qualification, awarding
body, subjects, self-reported confidence and optional latest results. It can also
inspect recent questions held in the current Streamlit browser session.

Its recommendations are transparent study-planning suggestions. They are not
predicted grades, admissions decisions, diagnoses or judgments of a student's
ability. A student may select a subject focus or let the Navigator use their own
confidence ratings.

## Chat history and privacy

Current implementation:

- The AI Teacher sends up to the most recent 12 turns in the current browser session
  to the configured AI provider.
- The Student Navigator can view a short list of recent user questions in that same
  session.
- Chat history is temporary and is not written to Supabase or used to train a model.
- The saved profile is used as context only when the student opts in on the AI Teacher
  page.
- The student can clear the current session's chat.
- Do not ask students for passwords, identity numbers, private records or sensitive
  personal information.

Persistent cross-session memory is not enabled. It should only be added after
implementing explicit opt-in, inspectable memory summaries, per-user row-level
security, retention limits and deletion controls. Raw conversations should not be
stored by default.

## Configure an AI provider

The adapter supports an OpenAI-compatible Chat Completions API. Add credentials only
to Streamlit Secrets, never to source control:

~~~toml
[ai]
base_url = "https://api.openai.com/v1"
api_key = "YOUR_PROVIDER_API_KEY"
model = "YOUR_TEXT_AND_VISION_CAPABLE_MODEL"
~~~

The provider must support image input for screenshot questions. Before enabling any
provider, the project owner must check its current age eligibility, privacy, data
handling, availability and pricing terms. Do not bypass provider age or account
eligibility rules. No provider key is included in this repository, and the AI Teacher
remains disabled until the provider is properly configured.

## Current limitations and next steps

- The registry already covers multiple systems, but many are represented by reviewed
  snippets or catalogues rather than complete subject specifications.
- The new adapter currently uses the existing TF-IDF engine. It does not fine-tune a
  model or claim perfect answers.
- Subject catalogue matches are explicitly labelled catalogue evidence, not complete
  specifications.
- The next research task is to add versioned, subject-specific specifications and
  examination-session grading documents, then expand the evaluation question set.
- Add persistent student memory only after the privacy and deletion workflow is
  implemented and tested.
