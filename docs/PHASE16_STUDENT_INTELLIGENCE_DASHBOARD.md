# Phase 16 — Student Intelligence Dashboard

## Purpose
Give learners a clear, honest view of their own recorded topic reflections and practice activity, without presenting self-reported information as formal grades.

## Delivered
- Add a Student Intelligence section to the existing Dashboard.
- Show topics tracked, recorded practice attempts, active study days in the last seven days and a consecutive-day learning streak.
- Visualise the latest topic-level descriptive signal, using practice accuracy only where attempts are recorded and confidence as a separate self-report component.
- Show the five lowest-signal topics as review priorities, with evidence labels and accuracy disclosure.
- Link directly to Student Navigator to continue a learning cycle.
- Add a pure analytics module with validation and unit tests.

## Method and limitations
For topics with recorded attempts, the descriptive signal is 60% recorded practice accuracy and 40% self-rated confidence. Without practice attempts, it is confidence × 20 and labelled provisional. Latest record per subject/topic is used. Study streak counts consecutive calendar dates with valid topic entries; it does not measure time spent or learning quality.

These values are not grades, diagnoses, admissions predictions or validated measures of mastery. The dashboard only reflects data that the learner has chosen to record in their profile. Empty data produces an explicit onboarding message rather than invented metrics.

## Privacy
The dashboard reads the existing learner profile in the authenticated session. It introduces no new external data collection or third-party analytics service.

## Release checks
- Run compilation and the complete unit-test suite.
- Verify empty-profile and populated-profile states.
- Verify invalid topic records are ignored.
- Test responsive layout on mobile and desktop.
- Confirm the profile remains private under the existing Supabase row-level security policies.
