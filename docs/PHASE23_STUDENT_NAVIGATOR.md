# Phase 23 — Action-first Student Navigator

## Product changes
- Replaces the Navigator's long introduction and multiple explanatory panels with a compact visual header.
- Brings one recommended next step to the top, with direct actions to open AI Teacher or the Study Planner.
- Uses learner-entered topic records to surface the highest-priority topic before generic planning suggestions.
- Keeps recent questions, source coverage and recommendation methodology available in short disclosures rather than leading with paragraphs and metrics.
- Moves topic entry into a compact disclosure and replaces the wide progress table with a few readable topic cards plus an optional full list.
- Preserves privacy, account ownership, opt-in profile saving, and the distinction between study signals and formal grades.
- Escapes learner-provided values before rendering them into HTML.

## Recommendation boundaries
- Uses only learner-selected subjects, self-reported confidence, recent browser-session questions and topic progress already available to the current account.
- Does not infer grades, admission chances, ability, diagnoses or likely examination outcomes.
- Source counts describe the reviewed registry only; they do not imply complete curriculum coverage.

## Validation
- Unit tests cover recent-question scope, low-confidence prioritisation, explicit focus selection and empty-profile guidance.
- CI must pass before merge.
- Live visual, navigation, mobile and account-isolation checks remain separate release checks.

## AI provider boundary
This phase does not activate Gemini or any other hosted model, request credentials, or change billing. Before a Gemini integration is considered, an authorised adult must verify current Google account/API eligibility, terms for a service intended for under-18 learners, data handling, quota, payment requirements and no-billing controls. Credentials must be added directly by that adult to deployment secrets, never pasted into chat or committed to GitHub.
