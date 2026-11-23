# Phase 26 — AI Teacher provider gate and privacy foundation

## What was verified
- The linked Supabase project `EduBridge-AI` is active and healthy.
- `student_profiles` has row-level security enabled and owner-only SELECT/INSERT/UPDATE/DELETE policies based on `auth.uid() = id`.
- The existing chat persistence code uses `student_chat_history`, but the table was absent. The table has now been created with RLS and owner-only policies. This migration is also checked into the repository for reproducible setup.
- Supabase security advisor reported one warning: leaked-password protection is disabled. An adult project administrator should review and enable it in Auth settings.
- The public feedback table allows anonymous/authenticated INSERT only with field validation; it does not grant public read access.

## Provider status — not activated
The Cloudflare credential was pasted into a chat. Treat it as compromised and revoke it in the Cloudflare dashboard immediately. This project intentionally contains no Cloudflare token, account secret, or API credential.

Cloudflare Workers AI documentation currently describes:
- A 10,000-Neuron daily free allocation on Workers Free; requests fail after the daily allowance is exceeded. Some models require a paid plan or prepaid credits.
- Workers AI Customer Content is processed to provide the service and is covered by Cloudflare's relevant subscription agreement and privacy policy. Cloudflare's documentation describes zero data retention for Customer Content except when other storage products/features are deliberately used.
- Individual model licenses and acceptable-use terms still apply.

Official references:
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/platform/data-usage/
- https://developers.cloudflare.com/workers-ai/

**Important unresolved requirement:** The public EduBridge audience includes school-age learners, including minors. The public documentation reviewed here does not provide a clear, explicit confirmation that this specific minor-facing tutoring application is permitted. Adult ownership of the Cloudflare account does not by itself answer whether the end-user audience is allowed. Do not configure or enable Cloudflare inference for the public app until Cloudflare confirms the use case in writing and the adult supervisor approves the applicable model license, privacy/consent process, retention, safety review and budget controls.

## Implementation boundary
- Existing local Ollama support remains available for adult-supervised, synthetic-data testing on the same machine.
- AI Teacher must continue to show a clear no-provider state when no eligible provider is configured.
- Do not claim a generative answer when the offline scaffold is used.
- Never place credentials in source, Git history, issues, logs, screenshots or chat.
- When provider eligibility is confirmed, use Streamlit server-side secrets and a narrow, dedicated token; never expose a token to the browser.

## Release checks
1. Revoke the exposed credential and create a replacement only if the adult supervisor has reviewed the provider terms and confirmed permission.
2. Confirm model-specific license and acceptable-use requirements.
3. Verify account budget controls and the hard stop after free allocation.
4. Test only with synthetic learner accounts/data until consent, safeguarding and privacy procedures are approved.
5. Run a two-account isolation test for profiles and chat history.
6. Test AI failure cases: invalid credentials, 401/403, quota exhausted, 429, timeout, malformed response, empty output and provider outage.
7. Keep public generative tutoring disabled until the provider gate is cleared.
