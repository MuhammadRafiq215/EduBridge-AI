# Phase 29 — Student Experience Redesign and Verification

## Delivered in this phase branch
- Subject Catalogue now has a clearer search-first layout, jurisdiction and awarding-body filters, and subject-family discovery (languages, mathematics/statistics, sciences, computing/technology, business/economics, humanities, arts, health/PE, vocational, religious/cultural studies).
- Catalogue cards distinguish an official catalogue review from a historical reference. This avoids presenting historical entries as current confirmed options.
- Academic Profile Analyzer now presents examination context, subject marks and result interpretation as three guided steps, with clearer mark-entry guidance.
- Global Knowledge Hub replaces the user-facing "Research pending" label and progress-count framing with source-record and jurisdiction summaries. Directory entries remain distinguishable from reviewed source notes; the UI does not falsely relabel unverified entries as verified.
- Career Pathways now has direct next actions to AI Teacher, Study Planner and compare another pathway.
- Added content and UI regression tests for the new subject-family discovery, career actions and knowledge-hub wording.

## AI Teacher and Guided Practice activation
Phase 28 provides the Cloudflare Workers AI OpenAI-compatible endpoint adapter. A live key has not been configured or tested by CI. The app reads provider settings from Streamlit's server-side `[ai]` secret section. Supabase settings belong in the separate `[supabase]` section and are used for learner authentication/profile storage, not provider credentials.

Cloudflare Workers AI Chat Completions base URL:
`https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1`
The adapter adds `/chat/completions`.

Cloudflare's documented minimum token permission for account AI endpoints is **Account → Workers AI → Read**, scoped to the one EduBridge account. Do not grant broad account, Workers edit, account settings, billing or API-token-management permissions. The token owner should be the adult project supervisor. Use an expiry and rotate/revoke tokens if exposed.

## Free usage and model selection
Cloudflare documents a 10,000-Neuron daily free allocation on Workers Free, with usage above that requiring Workers Paid. Some newer model IDs require paid billing. The previously used Kimi K2.7 Code model is listed among models requiring a paid billing method, so it is not suitable for a strict $0 setup. Confirm current model availability and pricing before selecting a model.

## Under-18 suitability and privacy
Cloudflare's Privacy Policy states that its own websites and services are not intended for individuals under 18, but separately says the policy does not apply to customers' applications and places responsibility for end-user privacy compliance on the customer. This is not by itself a blanket ban on customer applications. The adult project owner must still obtain written provider clarification on the intended school-age use, review applicable terms and privacy duties, and establish age-appropriate safeguards before enabling public learner traffic.

## Important safety limitation
The Cloudflare adapter does not have the OpenAI moderation endpoint. Do not enable public AI generation simply by setting `enabled = true`. Before public release, add and test provider-independent input/output safety screening, abuse limits, reporting and human escalation. CI cannot verify a live API token, provider terms, real account isolation, actual mobile rendering or Cloudflare quota/billing behaviour.

## Manual release checks
- Test two distinct Supabase accounts in separate browser sessions; verify profile, topic history, chat history and practice attempts never cross accounts.
- Sign out, switch accounts and use browser back/reload; private learner data must not reappear.
- Test Welcome, Navigator, Career Pathways, AI Teacher, Guided Practice, Subject Catalogue, Academic Profile Analyzer and Knowledge Hub on a narrow phone and laptop.
- Check empty states, long subject names, keyboard focus, touch targets, slow networks and provider error states.
- Verify the Streamlit deployment uses the latest merged `main` commit before declaring production completion.
