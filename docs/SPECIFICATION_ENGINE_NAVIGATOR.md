# Specification Engine and Student Navigator

## Architecture

The official Specification Engine is the evidence layer for EduBridge AI. The Student
Navigator uses learner-approved profile fields and temporary conversation context to
suggest next steps. The AI Teacher receives recent turns from the current browser
session plus relevant official-source excerpts.

~~~text
Learner profile + current-session conversation
                  |
                  v
           Student Navigator
                  |
                  v
Student focus / qualification / subject / year
                  |
                  v
       Official Specification Engine
                  |
        reviewed source records
                  |
                  v
       AI Teacher with evidence context
                  |
       answer + source references
~~~

## Specification record scope

Every record has an official source URL, issuer, qualification, country, awarding
body, topic, review date and approval status. Optional structured metadata classifies
the document type and records subject, version and effective period.

Document types currently supported:

- `qualification_overview`
- `subject_specification`
- `assessment_guidance`
- `grading_guidance`
- `recognition_guidance`
- `learning_resource`
- `other_official_guidance`

A qualification overview is not a subject specification. A grading notice is not
automatically valid for every exam year or series. If subject, version, effective
period or exam session is not recorded, the tutor must disclose that limitation and
ask for the applicable current official document. Never convert a broad overview
into a detailed syllabus, component weighting or grade threshold.

## Student Navigator

The Navigator uses only explicit profile information: qualification, country,
awarding body, level, subjects, self-reported confidence and optional results. It
can also see recent user questions held in the active Streamlit browser session.
Recommendations are deterministic planning suggestions, not grade predictions,
diagnoses, admissions decisions or a judgment of ability.

The Navigator does not infer private identity traits, store chat transcripts, or
silently add details to a learner profile.

## Conversation history and privacy

Current release behaviour:

- The AI Teacher sends up to the most recent 12 chat turns in the active browser
  session to the configured model provider.
- The Student Navigator can summarise recent questions from that same session.
- Chat history is temporary; it is not persisted in Supabase, used to train a model,
  or available after the browser session is cleared/ends.
- Profile context is used only when the learner opts in on the AI Teacher page.
- The app should never ask for passwords, identity numbers, private records or
  sensitive personal details.

Persistent cross-session learning memory is intentionally not enabled in this phase.
Before adding it, EduBridge needs an explicit opt-in, a clear memory summary that
students can inspect and delete, per-user row-level security, retention controls,
and an account deletion workflow. Do not store raw conversations by default.

## Current coverage

The knowledge base is a small starter collection. It includes broad official
overviews and guidance for Cambridge IGCSE, Pearson Edexcel International GCSE,
FBISE, Türkiye MEB and WAEC. It does not yet include comprehensive subject
specifications, all years/series, or all national and international qualifications.
The coverage dashboard reports counts and document types; those counts must never
be presented as complete board coverage.

## Next steps

1. Expand source collection with official subject specifications, assessment
   components, grading notices and qualification frameworks.
2. Add document version, effective date, exam series and subject metadata for each
   source where the issuer provides it.
3. Create an evaluation set of realistic student questions per qualification and
   test retrieval precision, citation correctness and scope errors.
4. Add semantic retrieval only after source quality and evaluation cases are strong.
5. Design opt-in persistent learning memory only after the privacy and deletion
   controls are implemented and tested.
