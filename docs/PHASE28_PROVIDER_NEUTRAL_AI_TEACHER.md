# Phase 28 — Provider-neutral AI Teacher activation

## Architecture
EduBridge's AI Teacher uses one shared chat-provider interface. Hosted providers that implement OpenAI-compatible Chat Completions can use the same adapter; changing providers means changing only the server-side endpoint, model identifier and credential. Cloudflare Workers AI is supported through its documented account-scoped OpenAI-compatible endpoint:

`https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1`

The adapter appends `/chat/completions`. Example model IDs are provider/model-specific and must be selected from the current model catalogue and licence terms.

## Safe activation gate
Hosted generation now remains disabled unless `[ai].enabled = true` is explicitly configured. This is deliberate. Do not enable it until the adult project supervisor has reviewed:
- the provider's current terms and written confirmation for the intended 13–17 learner-facing service;
- the selected model's licence and usage restrictions;
- data processing, retention, subprocessors and logging;
- content-safety controls, reporting and adult escalation;
- quota, rate limits, budget caps and automatic billing behaviour.

A provider's email verification, free tier, or zero-retention statement is not proof of suitability for a minor-facing public product.

## Streamlit Community Cloud secrets
Keep secrets in the Streamlit app's server-side Secrets settings. Never place them in GitHub, source files, browser code, learner profiles, chat-history rows or this conversation.

For a future adult-approved Cloudflare Workers AI setup:

```toml
[ai]
enabled = false
provider = "cloudflare_workers_ai"
api_key = "REPLACE_IN_STREAMLIT_SECRETS_ONLY"
base_url = "https://api.cloudflare.com/client/v4/accounts/REPLACE_ACCOUNT_ID/ai/v1"
model = "REPLACE_WITH_APPROVED_MODEL_ID"
timeout = 60
```

The value remains `false` until the approval gate above is complete. Do not copy a real token into this example or commit real secrets.

For another OpenAI-compatible service, set `provider = "openai_compatible"` and use that provider's official HTTPS base URL and approved model. The generic adapter rejects non-HTTPS endpoints and embedded credentials/query strings.

## Current limitations
- Cloudflare Workers AI uses the shared OpenAI-compatible adapter, but the provider-specific moderation path is not configured by this change. The adapter's OpenAI moderation calls apply only to the official OpenAI endpoint. Other providers must not be assumed to have equivalent screening.
- The AI Teacher currently keeps vision disabled for Cloudflare and other hosted providers unless a separately reviewed image-safety path is implemented.
- This change does not activate inference, validate a live token, or prove age-policy eligibility.
- Existing offline practice scaffolds remain explicitly labelled offline and do not pretend to generate or grade with AI.
- Learner IDs and account ownership remain managed by the existing authenticated account layer; provider credentials are never associated with individual student IDs.

## Tests
- Hosted providers remain disabled unless explicitly enabled.
- Cloudflare's account-scoped endpoint is accepted by the shared adapter.
- Invalid Cloudflare endpoints are rejected.
- Existing provider request, timeout, moderation and learner-context tests remain in place.
