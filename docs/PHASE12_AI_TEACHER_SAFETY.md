# Phase 12 — AI Teacher safety and OpenAI readiness

## What this phase changes
- Adds OpenAI's free Moderation API screening for text input and generated text when the official OpenAI endpoint is configured.
- Screens the learner's latest text before generation and screens the generated answer before it is displayed.
- Fails closed if moderation cannot be reached or returns an unreadable response.
- Adds an age-appropriate AI Teacher notice and safer system-prompt guidance.
- Keeps OpenAI image uploads disabled until an image moderation and human-review workflow is implemented.
- Removes an unverified live-app URL from the site footer. Only the verified repository link is shown.

## OpenAI configuration (adult-managed only)

The AI Teacher already reads its provider settings from Streamlit Secrets. A parent/guardian or other authorised adult who owns and manages the API organisation must review current OpenAI terms, the under-18 API guidance, privacy and data-retention settings, local legal requirements, and the app's safeguards before enabling it.

Example Streamlit Secrets structure:

```toml
[ai]
provider = "openai_compatible"
model = "MODEL_AVAILABLE_TO_THE_ADULT_ACCOUNT"
base_url = "https://api.openai.com/v1"
api_key = "PASTE_KEY_DIRECTLY_IN_STREAMLIT_SECRETS"
timeout = 60
supports_vision = false
```

This is a configuration template, not a real key. Never send a key in ChatGPT, a GitHub issue, a pull request, source code, README, commit, screenshot or public discussion. The adult account owner must create and manage the key and enter it directly into the hosting provider's secret manager. Rotate and revoke credentials if they are exposed.

## Cost: important $0 limitation

OpenAI's Moderation API is documented as free to use. Text generation through the OpenAI API is separately priced by model and token use. New API accounts use prepaid billing; the official setup guide currently requires payment details and a minimum initial credit purchase. Eligible Pro and Business subscriptions may receive API credits, but this is not a benefit for every ChatGPT Free account.

Therefore, this repository does not claim that OpenAI text generation can be activated with a guaranteed $0 balance or without billing details. Do not enable generation unless the adult account owner has explicitly approved the cost and spending controls. If the project must remain strictly $0, leave the hosted OpenAI provider disabled and continue using the local model path for supervised testing.

## Under-18 safeguards still required before public use

Moderation screening is only one safeguard. It does not make the product automatically compliant or production-ready. Before opening an AI Teacher to student users, the adult project owner must:
- Review OpenAI's current Under-18 API guidance and obtain any required parent/guardian consents.
- Publish a clear age-appropriate AI disclosure and privacy notice.
- Define a human review and reporting process for safety concerns.
- Test the system against prompt injection, unsafe requests, false positives and false negatives.
- Set reasonable rate and usage limits and monitor operational issues without collecting unnecessary student data.
- Review applicable Pakistan and other users' local child-protection and privacy requirements.
- Keep profile sharing and persistent chat history opt-in; do not collect sensitive personal details.
- Review provider retention controls. API data is not used for model training by default, but abuse-monitoring logs may be retained for up to 30 days under standard settings.

## Test and release gates
- [ ] GitHub Actions compile and unit tests pass.
- [ ] OpenAI input moderation runs before generation.
- [ ] OpenAI output moderation runs before display.
- [ ] Moderation outage blocks hosted generation (fail-closed).
- [ ] OpenAI screenshot uploads remain disabled.
- [ ] Local provider tests continue to pass.
- [ ] Adult owner has reviewed terms, consent, budget, privacy and safeguards.
- [ ] Human reporting/review workflow is operational.
- [ ] Live app is tested on desktop and mobile before public release.

## Official references
- [OpenAI Under-18 API guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance)
- [OpenAI Moderation guide](https://developers.openai.com/api/docs/guides/moderation)
- [OpenAI safety best practices](https://developers.openai.com/api/docs/guides/safety-best-practices)
- [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data)
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- [OpenAI API billing setup](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform)
- [OpenAI Services Agreement](https://openai.com/policies/services-agreement/)
