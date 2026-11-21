# Phase 10 — Cloud AI readiness

## Goal

Prepare the existing EduBridge AI Teacher for a hosted deployment without activating a provider, creating credentials, or changing the current local-model workflow. The hosted provider remains disabled until an adult account owner has reviewed the provider's current eligibility, service terms, privacy/retention terms and pricing, and explicitly approves setup.

## Existing architecture retained

- Streamlit remains the application runtime.
- `src/ai_teacher.py` remains the provider adapter.
- `src/ai_teacher_ui.py` continues to call the provider only when valid server-side settings are present.
- The specification engine continues to prepare source-grounded context before model invocation.
- Supabase learner profiles and optional chat history remain separate from model-provider credentials.
- Local Ollama-compatible mode remains available for same-computer development.

## Hosted deployment configuration

Hosted settings are read server-side from Streamlit secrets. Never add secrets to Git, source files, browser code, issue comments, chat messages, or screenshots.

After provider approval, an administrator may configure the following shape in the hosting platform's secret manager:

```toml
[ai]
provider = "openai_compatible"
api_key = "ADMIN_CONFIGURED_SECRET"
model = "ADMIN_APPROVED_MODEL_ID"
base_url = "https://api.provider.example/v1"
timeout = 45
supports_vision = false
```

This is a template, not an active provider configuration. The endpoint and model must come from the provider's official documentation. Use only HTTPS for hosted endpoints. Do not set vision support unless the selected model and provider terms explicitly support it and the feature has been reviewed.

## Deployment gates

A parent/account owner must complete these checks before enabling a hosted provider:

1. Confirm the provider permits the account holder to create and operate the API account under its current age and account rules.
2. Confirm the provider permits the intended student-facing educational application and its expected user age range.
3. Review data processing, retention, training use, regional handling, safety and acceptable-use terms.
4. Confirm pricing, free-tier limits, rate limits and any billing controls. Do not assume that an API is free.
5. Create and store credentials only in the hosting platform's secret manager; do not share the key with the learner or put it in the repository.
6. Configure conservative request limits and monitor usage. A free budget means the hosted model must remain disabled if no genuinely free, permitted option exists.
7. Test with synthetic, non-sensitive questions before any real learner profile or student data is sent.

## Privacy and safety defaults

- Keep learner-profile sharing off unless the learner explicitly opts in.
- Keep persistent chat history off by default.
- Do not transmit email addresses, account identifiers, passwords, identity numbers, or unrelated profile fields as model context.
- Avoid collecting age or date of birth in the AI chat.
- Display a clear notice that hosted prompts are sent to the selected provider.
- Provide a clear unavailable state when no approved provider is configured; never fabricate an AI answer.
- Keep model credentials exclusively in server-side secrets.
- Do not expose a provider key through logs, error messages, analytics, or UI.

## Verification checklist

- [ ] Existing unit tests pass.
- [ ] Hosted endpoint validation accepts HTTPS and rejects HTTP, malformed URLs, embedded credentials, query strings and fragments.
- [ ] API key is never displayed or written to logs.
- [ ] Missing provider settings show the existing honest unavailable state.
- [ ] Local mode still works on the same computer as its model runtime.
- [ ] Cloud deployment does not attempt to contact the developer laptop's localhost.
- [ ] Supabase authentication and RLS are verified in the actual project.
- [ ] Adult account owner approves provider terms and secret configuration.
- [ ] Live provider test uses synthetic data and a confirmed $0 budget.

## Current status

This phase adds deployment-readiness safeguards and documentation only. No provider account, API key, billing arrangement, or live cloud model is enabled by this change.
