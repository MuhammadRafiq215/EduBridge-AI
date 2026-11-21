# Phase 18 — AI Teacher Runtime Activation & End-to-End QA

## Release objective
Prove the complete learner journey works from subject/topic selection through reviewed-source retrieval, provider generation, citation display, safe failure handling and optional progress recording.

This phase distinguishes three states:
1. **Offline source helper:** reviewed-source search only; no generated tutoring.
2. **Configured runtime:** a provider is configured but live connectivity has not yet been confirmed.
3. **Verified runtime:** an authorised adult-managed provider has passed the supervised smoke tests below.

Never display "AI connected" merely because a secrets file contains settings.

## Current implementation verified in repository
- Provider-independent adapter supports a local Ollama-compatible runtime and an OpenAI-compatible hosted runtime.
- Official OpenAI endpoint invokes moderation before generation and screens the generated answer; moderation failure blocks generation.
- Official OpenAI image input is disabled.
- Conversation context is limited to the last 12 text messages.
- Learner context is allow-listed.
- Specification context is marked untrusted; the tutor is instructed to cite only source IDs present in retrieved evidence.
- AI Teacher clearly presents an offline source helper when no provider is configured.
- Guided Practice uses a labelled offline scaffold rather than pretending to generate/mark questions without a model.

## Important boundary
No live provider credential is stored in this repository. Do not put API keys in Git, issue comments, chat, screenshots or test fixtures. A parent/guardian or authorised adult must review provider terms, consent, privacy, expected cost and account ownership, then place any approved secret directly in Streamlit Community Cloud's secret manager. Never request or commit the service-role Supabase key.

OpenAI moderation is an additional safeguard, not complete protection. Before learner-facing use, add and test a clear report/feedback path, a human review/escalation owner, privacy/retention notices, rate limits, prompt-injection tests and an incident response procedure. No live rollout to minors until required guardian consent and applicable legal requirements have been reviewed.

## Automated tests
`tests/test_ai_teacher_runtime_readiness.py` uses mocked HTTP responses only. It checks provider configuration boundaries, vision disabled for official OpenAI, loopback-only local runtime, untrusted-source/citation prompt constraints, bounded conversation history and fail-closed moderation.

These tests do not prove provider uptime, factual accuracy, citation correctness in real outputs, latency, or live deployment.

## Supervised end-to-end test plan
Run only after the adult project owner approves and configures the provider.

| ID | Test | Expected result |
|---|---|---|
| E2E-01 | Open app with no AI secrets | Explicit offline source-helper state; no false connected badge |
| E2E-02 | Ask a known qualification/source question | Relevant source record and official link shown, or honest no-match message |
| E2E-03 | Ask a subject concept question with provider disabled | No generated answer claim; offline mode is clearly explained |
| E2E-04 | Configure approved provider in hosting secrets | App loads provider settings without exposing secret |
| E2E-05 | Ask a simple subject question | Answer is returned, understandable and age-appropriate |
| E2E-06 | Ask a board-specific question with matching official record | Only matching source IDs cited and source links visible |
| E2E-07 | Ask a board-specific question with no matching record | Tutor distinguishes general explanation from verified board rule |
| E2E-08 | Submit untrusted text embedded in retrieved source | It is treated as source text, not instructions |
| E2E-09 | Cause provider timeout / 401 / 429 in staging | Clear non-secret error; no traceback or credential disclosure |
| E2E-10 | Simulate moderation unavailable | Generation blocked |
| E2E-11 | Inspect chat history with persistence disabled | No durable chat history saved |
| E2E-12 | Inspect learner profile sharing disabled | Profile context not shared beyond selected feature flow |
| E2E-13 | Test phone width and desktop width | Sidebar, chat, citations, forms and buttons remain usable |
| E2E-14 | Navigate every workspace and all Explore Tools pages | No broken navigation or hidden destinations |
| E2E-15 | Record a practice attempt and open Student Intelligence | Only real saved/available activity appears; no invented mastery score |

## Go / no-go gates
- GitHub Actions compilation and unit tests green.
- Adult owner approves provider, consent and budget.
- Hosting secret is set by the adult owner; no credential appears in Git or logs.
- Supervised smoke test passes.
- Source citations checked against the actual retrieved records.
- Error states, mobile layout and navigation manually verified.
- Reporting/escalation and privacy disclosures reviewed.
- Document limitations: AI can be wrong; source coverage is incomplete; progress indicators are not formal grades.

## Rollback
Remove the AI provider secret in Streamlit Community Cloud and redeploy. The app must return to the explicitly labelled offline source helper. Do not delete learner records or alter Supabase auth credentials as a rollback shortcut.
