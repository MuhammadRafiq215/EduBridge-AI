# Phase 20 — AI Teacher and learner journey

## Product objective
Make the AI Teacher feel like a focused study workspace: a clear conversation surface, course context available when useful, concise starter actions, and visible privacy/safety controls without crowding the learner.

## Interface changes
- Replaces the long hero description and three decorative claims with a short learning promise.
- Moves source coverage counts and caveats into a collapsed disclosure.
- Shortens the offline-mode explanation while retaining the critical distinction between source search and generated tutoring.
- Uses the selected subject in the starter prompts.
- Moves privacy guidance into a compact disclosure.
- Constrains chat surfaces to a readable maximum width and adjusts spacing on narrow screens.
- Keeps provider status honest; no synthetic AI replies or fake connected state are introduced.

## Runtime and supervision boundaries
This phase does not add credentials, API keys, paid provider activation, or automatic external calls. Existing provider configuration remains controlled by the adult operator in the deployment environment. Never commit secrets or send them in chat. A production hosted model must be explicitly approved by the responsible adult after reviewing provider terms, budget, learner consent, privacy/retention, data location and applicable rules.

Moderation is one safeguard, not a complete child-safety programme. Before a student pilot, the operator must define human escalation and reporting, age-appropriate use rules, abuse monitoring, rate limits, retention/deletion, incident response and guardian/school contact routes.

## Supervised runtime test plan
Run only with an adult supervisor and a test account containing no real student personal data.

1. Confirm provider is unconfigured: UI clearly identifies source-search mode and never claims generative tutoring.
2. Confirm authorised provider configuration: status/model label matches actual configured provider.
3. Test subject awareness with two different subjects and qualification contexts; verify no context leakage between accounts/sessions.
4. Test concise explanation, worked example, misconception correction, hint-first tutoring, one-question-at-a-time practice and feedback after learner attempt.
5. Test verified-source citations; confirm absent evidence is disclosed and unsupported exam rules are not invented.
6. Test prompt injection embedded in retrieved source records; retrieved content remains untrusted data.
7. Test moderation input/output blocks and fail-closed behaviour where applicable.
8. Test provider timeout, unavailable endpoint, authentication failure, rate limit and malformed/empty response. Errors must be clear, bounded and must not expose secrets.
9. Verify chat history is temporary by default, opt-in when signed in, scoped to the correct account and deletable.
10. Verify profile context is opt-in and allow-listed; image uploads remain disabled unless the selected provider explicitly supports them and safety checks permit them.
11. Verify the interface on phone and laptop, keyboard navigation, focus visibility, long messages, empty states and network errors.

## Full learner-journey QA
- First visit and Welcome actions
- Account sign-up/sign-in/reset and signed-out mode
- My learning profile save/edit/export/delete and opt-in boundaries
- AI Teacher source-only and configured-provider states
- Student Navigator recommendations and source coverage disclosures
- Guided Practice offline and model-assisted paths
- Topic progress, adaptive priorities and revision schedule
- Study planner and career pathways
- Global Research Lab indicator selection, missing data and source-year labels
- Feedback submission and privacy notice
- Sidebar/page navigation, browser refresh, mobile viewport and session/account switching

## Go/no-go criteria
Do not invite students until: automated checks pass; a supervisor completes the runtime plan; no secrets appear in repository/history/logs; privacy and safeguarding notices are reviewed; data deletion and reporting routes are tested; all critical navigation paths work; and mobile/laptop visual checks are recorded. A passing CI run alone is not proof of live provider safety or production readiness.

## Known limits
Automated tests do not replace live supervised tests. A local model bound to localhost is only reachable from the same machine running the app; it is not a hosted Streamlit Cloud runtime. Provider terms and pricing must be checked at the time of activation.
