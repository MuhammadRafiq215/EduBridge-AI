# Phase 31 — AI Gateway Guardrails, Guided Practice and Visual Refinement

## Delivered in this branch
- Cloudflare Workers AI requests can only proceed when an AI Gateway ID is supplied and the deployment explicitly confirms that Guardrails has been configured.
- Cloudflare requests carry the `cf-aig-gateway-id` header.
- Chat requests explicitly use non-streaming mode so Gateway response enforcement can apply.
- Generation is bounded with a 900-token maximum.
- Added regression tests for fail-closed configuration, gateway routing, non-streaming requests and secret-safe errors.
- Refined the shared Aurora visual palette with deeper ink, calmer surfaces, teal accents and consistent gradients.

## Required Cloudflare dashboard setup before enabling
1. Create or select an AI Gateway for the same Cloudflare account.
2. Enable Guardrails for that gateway.
3. Configure all applicable content-hazard categories S1–S14 to **Block** for prompts and responses.
4. Configure prompt-injection category P1 to **Block** for prompts.
5. Keep request streaming disabled.
6. Confirm the gateway policy is active and review the provider terms, privacy notice, age suitability, retention and incident-response arrangements with the adult supervisor.
7. Add `safety_gateway_id` and `guardrails_enabled = true` to the server-side `[ai]` settings only after those steps have actually been completed.

The `guardrails_enabled` value is an explicit deployment attestation, not an automatic remote verification of the dashboard policy. Do not set it to true before the gateway policy is configured and reviewed.

## Configuration additions
- `safety_gateway_id`: the AI Gateway identifier, commonly `default` if using the default gateway.
- `guardrails_enabled`: must remain false or absent until the required policy is active.

## Safety and release status
- Existing `enabled = false` remains the recommended setting until dashboard configuration and supervised end-to-end checks are complete.
- This branch does not claim that a saved token proves a working or safe deployment.
- Gateway Guardrails uses Workers AI and therefore consumes usage. The published free allocation is 10,000 Neurons/day; usage above the free allocation on a paid plan is billed. Monitor usage and configure limits before any student pilot.
- The screening models are classifiers, not guarantees. Maintain reporting, human oversight and conservative failure handling.
- Guided Practice continues to call the same provider interface; when Cloudflare is configured, its generation requests inherit the same Gateway Guardrails route.

## References
- Cloudflare AI Gateway Guardrails: https://developers.cloudflare.com/ai-gateway/features/guardrails/
- Guardrails usage, hazard categories and streaming limitations: https://developers.cloudflare.com/ai-gateway/features/guardrails/usage-considerations/
- Workers AI REST API and gateway selection: https://developers.cloudflare.com/ai-gateway/usage/rest-api/
- Workers AI pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
