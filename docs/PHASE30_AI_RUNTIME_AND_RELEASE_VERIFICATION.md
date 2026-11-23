# Phase 30 — AI Teacher, Guided Practice and Release Verification

## Current implementation status
- Phase 29 is merged into `main`.
- Phase 30 introduces a fail-closed runtime gate for Cloudflare Workers AI. Its OpenAI-compatible chat endpoint does not automatically provide the input/output moderation endpoint used by the official OpenAI adapter.
- Until a separately reviewed and tested safety-screening layer is implemented for Cloudflare, EduBridge refuses to send student prompts to Cloudflare. This is intentional; a configured API token is not evidence that a teen-facing service is safe.
- Guided Practice already builds bounded, subject-aware prompts and retains an offline scaffold. It must not claim AI-generated questions or feedback when no approved provider is available.
- No API credentials are stored in this repository or test fixtures. Tests use synthetic placeholders only.

## Cloudflare token scope clarification
Use the Cloudflare Workers AI dashboard's dedicated **Use REST API → Create a Workers AI API Token** flow when possible. If creating a custom token, follow the current Cloudflare REST API documentation and review the prefilled permission set; current docs state that a manually created token may need Workers AI Read and Workers AI Edit. Scope the resource policy to the single account whose Account ID appears on the Workers AI page, not all accounts. Account scope is not a Streamlit or Supabase setting.

## Streamlit secret placement
Store provider configuration in Streamlit Community Cloud server-side Secrets under `[ai]`. Keep Supabase authentication settings separately under `[supabase]`. Never commit tokens, put them in frontend code, or send them in chat. If a token was ever exposed, revoke it and create a replacement.

## Remaining Phase 30 work
1. Implement a provider-independent input/output safety-screening interface and an approved Cloudflare-compatible screening implementation; fail closed on screening timeout, malformed output or provider outage.
2. Add tests for prompt injection, harmful/unsafe content handling, refusal behaviour, screening outages, provider 401/403, 429, timeout, malformed response and oversized input.
3. Wire Guided Practice question generation and feedback through the same screened provider interface. Preserve clear labels between AI-generated feedback and learner self-reflection; never imply an official grade.
4. Add request limits, output-length bounds, safe logging (no prompts, tokens, or learner identifiers in ordinary logs), and human reporting/escalation guidance.
5. Verify account isolation with two synthetic Supabase accounts; verify sign-out, account switching, history deletion and session cleanup.
6. Run full navigation and responsive checks on phone and laptop, including AI Teacher, Guided Practice, Career Pathways, Subject Catalogue, Profile Analyzer and Knowledge Hub.
7. Deploy only after adult supervisor approval of provider terms, age suitability, privacy notice/consent, screening, limits, and incident response.

## Release gate
A successful GitHub CI run is necessary but not sufficient for production. Do not enable Cloudflare generation publicly until provider-specific screening is actually wired, tested and reviewed. Do not expose credentials in source control or client-side UI.
