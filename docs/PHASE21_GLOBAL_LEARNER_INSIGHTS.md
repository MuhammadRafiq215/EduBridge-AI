# Phase 21 — Global learner insights and responsive chat controls

## Changes
- Replaces the fixed 20-country list with the live World Bank country/economy catalogue, excluding regional and income aggregates.
- Allows comparison of up to 20 selected economies at once. The source may expose reporting economies and territories as well as sovereign states; the interface labels the catalogue accordingly.
- Retains the observation year and distinguishes missing observations from zero values.
- Removes the historical Portuguese-school ML experiment from the student-facing Research Lab.
- Replaces it with private learner insights calculated from the current learner profile's topic-progress records.
- Passes the current profile to the Research Lab renderer; no learner records are sent to the World Bank or published as a public comparison.
- Adds Compact, Balanced and Wide conversation-width controls to the AI Teacher. Phone layouts remain full-width, and Streamlit session state preserves the selected width during reruns.
- Adds automated tests for World Bank country-catalogue parsing and aggregate exclusion.

## Data boundaries
World Bank country metadata and education indicator observations are public country-level data. Country coverage depends on the World Bank catalogue and individual indicator reporting. Not every country has a value for every indicator or year. Missing values are not zero.

Personal insights are calculated from the signed-in learner's own profile records supplied to the Research Lab. They are not a public ranking, formal grade, diagnosis or prediction. Anonymous sessions without saved profile topic records see a prompt to record a topic in Student Navigator.

## Verification still required
- CI must pass before merge.
- Live World Bank API test: country list loads, selected indicators return values/years, missing data and network errors render safely.
- Verify country selector on phone and laptop, including search and maximum selections.
- Verify personal insights only use the active learner profile; switch accounts and confirm no cross-account data remains.
- Verify chat width controls survive message submission, reruns and browser navigation; test Compact/Balanced/Wide on laptop and full-width behaviour on phone.
- Verify the old ML experiment and its dataset/metrics no longer appear in the Research Lab.
- Complete supervised AI runtime and full navigation QA before inviting students.

## Release gate
This phase does not activate any provider, add API credentials or run live AI generation. Student access remains gated on adult-supervised runtime tests, privacy/safeguarding review and complete learner-journey QA.
