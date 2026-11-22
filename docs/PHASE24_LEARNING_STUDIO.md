# Phase 24 — Learning Studio redesign and subject catalogue

## Product intent
Make the learner experience feel like one coherent learning studio: clear hierarchy, calm backgrounds, strong contrast, readable cards, responsive controls and fewer dead ends. The visual direction takes general usability lessons from recognised learning products and current education-site galleries: progress at a glance, clear next actions, focused learning tasks, approachable visual hierarchy and responsive layouts. EduBridge uses its own identity; it does not copy another product's screen, logo, illustrations or proprietary layout.

## Delivered in this phase
- Refines the shared visual system with layered paper-like backgrounds, more consistent input/expander/chat surfaces, responsive spacing, hover feedback and reduced-motion support.
- Makes the Student Navigator usable before a learner has completed a profile: choose a subject from the catalogue and receive a starting recommendation without having to leave the page.
- Adds at-a-glance subject, topic-record and study-signal metrics.
- Expands Record a topic and Guided Practice to use the international subject catalogue already maintained in `src/global_education.py`, while retaining learner-entered subjects.
- Adds a custom subject field in both flows so learners are not blocked by catalogue gaps.
- Adds unit tests for catalogue breadth, deduplication, personal subjects and malformed profile values.

## Subject catalogue limitations
The catalogue is a broad discovery list, not proof that every listed subject is available in every country, school, exam board or session. Learners should still confirm their exact qualification, subject code and current specification with the awarding body. Custom subjects remain available.

## AI Teacher and provider decision
- AI Teacher continues to support the local Ollama-compatible mode for supervised local testing and the existing reviewed-source search when no generative provider is configured.
- This phase does not enable a cloud model or request/store API credentials.
- Gemini API terms effective March 23, 2026 require API users to be 18+ and prohibit use in API clients directed to or likely to be accessed by under-18s. It is not an eligible provider for EduBridge's intended audience.
- Hugging Face's account terms permit account registration from age 13, but Inference Providers pricing documentation is not a stable guarantee of a free production allowance: its current pricing documentation says free users have no included inference credits and require purchased credits to use routed inference. Individual routed providers also have their own data and use terms. Do not treat this as a confirmed $0 production provider.
- OpenAI publishes explicit under-18 API safeguards guidance, but its generation API is paid. It is not compatible with the project's strict $0 production budget unless an authorised organisation funds it.
- Therefore the public generative AI Teacher remains disabled until an eligible provider, terms for minor end users, privacy, data retention, moderation, quota and a genuine no-billing limit are all verified by an authorised adult.

## Validation and release gates
- Run the full repository CI suite.
- Verify desktop and mobile layout on the deployed app.
- Test catalogue selection, custom subjects, topic saving, practice creation, account switching and profile privacy with synthetic accounts.
- Test AI Teacher local mode on the same computer as its model server. Do not expose a local model port publicly.
- CI passing does not replace live browser, accessibility, privacy or adult provider-terms review.
