# Phase 14 — Generative AI Teacher readiness

## Scope
This phase connects the existing AI Teacher interface to the provider adapter already used by EduBridge and carries forward the under-18 safety work. It does not create API credentials, enable paid generation, or claim that a hosted model is online.

## Generative tutoring flow
1. The learner chooses qualification, country, awarding body, subject, year and exam series.
2. EduBridge retrieves matching reviewed specification records and relevant subject catalogue mentions.
3. The application builds a bounded evidence context with source IDs, issuer, qualification, jurisdiction, status, review date, official URL, notes and limits.
4. The provider receives the learner's recent conversation, optional explicitly enabled education profile context, and the evidence context.
5. The tutor is instructed to explain concepts step by step, distinguish verified evidence from general teaching, avoid unsupported exam-board claims and cite only source IDs present in the evidence.
6. The UI shows retrieved official records in a separate source panel so learners can open and verify the original material.

## Safety controls carried into this phase
- Official OpenAI endpoint: screen latest learner text before generation and generated answer before display using the Moderation API.
- Fail closed if the moderation endpoint is unavailable or returns an unreadable response.
- Age-appropriate system instructions and trusted-adult escalation language.
- OpenAI image uploads remain disabled.
- Learner text input is capped at 4,000 characters.
- Conversation context is limited to the latest 12 turns.
- Retrieved source context is capped at 18,000 characters and explicitly treated as untrusted reference data, not instructions.
- Profile context remains allow-listed and opt-in.
- Chat history remains optional and off by default.

## Provider and deployment configuration
The provider reads its configuration from Streamlit Secrets. Do not place credentials in source code, GitHub, issue comments, screenshots or ChatGPT. The adult project owner must review provider eligibility, terms, parent/guardian consent, privacy, retention, budget and local legal requirements, then enter any approved credential directly into Streamlit Secrets.

Example shape only (not a real key):
```toml
[ai]
provider = "openai_compatible"
model = "MODEL_SELECTED_BY_THE_ADULT_ACCOUNT_OWNER"
base_url = "https://api.openai.com/v1"
api_key = "ENTER_DIRECTLY_IN_STREAMLIT_SECRETS"
timeout = 60
supports_vision = false
```

## Cost and $0 constraint
OpenAI's Moderation API is free to use. Ordinary model generation is separately priced according to the selected model and token use. Therefore, the hosted OpenAI provider must remain disabled while the project budget is strictly $0. ChatGPT Free access does not itself provide a free OpenAI API generation balance.

A local model can be used for supervised development when Streamlit and the local model server run on the same computer. A Streamlit Cloud app cannot connect to a model server on a student's phone or laptop through localhost.

## Release gates before real student use
- [ ] Adult project owner has reviewed the current OpenAI under-18 API guidance and service terms.
- [ ] Required parent/guardian consent is in place.
- [ ] A privacy notice and age-appropriate AI disclosure are published.
- [ ] A human reporting and review route is operational.
- [ ] Prompt-injection, unsafe-input, unsafe-output, no-source, wrong-subject, wrong-session and moderation-outage cases are tested.
- [ ] Rate limits, spending limits and provider retention settings are reviewed.
- [ ] CI passes and the deployed site is tested on mobile and desktop.
- [ ] Live generation is enabled only after explicit adult approval of provider and budget.

## Official references
- OpenAI under-18 API guidance: https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance
- OpenAI moderation and safety best practices: https://developers.openai.com/api/docs/guides/safety-best-practices
- OpenAI Chat Completions API reference: https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create
- OpenAI API pricing: https://developers.openai.com/api/docs/pricing
