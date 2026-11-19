# EduBridge AI — Student pilot guide

## Purpose

This is a small usability and reliability pilot, not a study of student ability or a validation of an academic prediction system. Ask a small group of students to explore the public learning features and report what is clear, confusing, useful or broken.

## Before inviting testers

- Confirm the latest GitHub Actions workflow is green.
- Open the deployed Streamlit URL in a private/incognito window and on a phone.
- Confirm the Dashboard, Career pathways, Study planner and Research insights pages load.
- Run the Research Lab experiment once and verify that real results appear.
- Test PDF profile export using a non-sensitive sample profile.
- Confirm the Account & privacy page explains what is stored and that the app never asks for identity numbers or private documents.
- Run supabase/feedback_schema.sql in the Supabase SQL Editor to enable anonymous in-app feedback. This creates a separate table and does not change student_profiles.
- Submit one test feedback entry, then inspect it using the SQL query at the bottom of that SQL file.

## Suggested tester tasks

Ask each tester to try the following, in order:

1. Open the Dashboard and explain what they think EduBridge AI helps with.
2. Open Career pathways and explore one field.
3. Find one degree direction and one starter project.
4. Open My learning profile and understand which information is optional.
5. Open Study planner and check whether the weekly plan is understandable and realistic.
6. Open Research insights and identify what the public dataset does and does not represent.
7. Find the privacy explanation and describe what they think is stored.
8. Submit feedback from the Student feedback page.

Testers do not need to create an account to explore public pages or submit feedback. Account registration is optional. Anyone under 18 should involve a parent or guardian before creating an online account.

## Feedback rules

Please ask testers not to submit full names, phone numbers, email addresses, home addresses, school IDs, identity-card numbers, passwords, private documents, grades or information about another identifiable student.

The feedback form stores the selected page, category, 1–5 experience rating and written suggestion. It does not ask for names or contact details. Submitters cannot read the feedback table. Only the project owner can review submissions through the Supabase SQL Editor. Review feedback regularly and delete records when they are no longer needed.

## Pilot scorecard

| Area | What to observe |
|---|---|
| First impression | Can the tester explain the purpose quickly? |
| Navigation | Can they find each main workspace? |
| Clarity | Are labels and instructions understandable? |
| Usefulness | Does the pathway or planner help them decide a next step? |
| Trust | Are research limitations and privacy notices clear? |
| Reliability | Any error, blank page, slow load or broken action? |
| Mobile | Can they use the site comfortably on a phone? |

## Release decision

Do not describe the app as error-free or production-validated based only on unit tests. Follow the first pilot with bug fixes, a second round of testing and a final review of privacy, Supabase access policies and Streamlit logs.
