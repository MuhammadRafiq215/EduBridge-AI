# Phase 22 — Learner-first interface and supervised pilot readiness

## Interface scope
- Rebuilds Welcome as a vibrant, compact learning home with clear primary destinations and a three-step learning rhythm.
- Uses responsive card grids, high-contrast gradient surfaces and concise action labels.
- Simplifies Student Navigator's introduction, moves detailed source and safety information into disclosures, and shortens Guided Practice descriptions.
- Preserves safety-critical information: AI is a study aid, personal secrets should not be shared, and important exam facts need official-source verification.
- Does not change provider activation or imply that generative AI is connected.

## Supervised AI Teacher runtime checklist
Use a test account and synthetic educational examples only. An authorised adult must operate provider configuration and supervise the session.

### Provider and cost
- Confirm provider terms permit the intended product, age group, jurisdiction and deployment model.
- Confirm the exact free-tier quota, rate limits, data controls, retention, model-training policy and whether a payment method is required.
- Ensure no paid fallback, auto top-up or automatic billing can occur. Set a hard application-side request cap where supported.
- Store credentials only in deployment secrets managed by the adult. Never commit or paste credentials into chat.
- Test unconfigured state, valid configuration, invalid key, quota exhausted, rate limited, timeout, DNS/network failure, malformed response and provider outage.
- Errors must be safe, short, recoverable and must not reveal credentials, stack traces or private prompt contents.

### Teaching quality
- Test multiple subjects, qualification levels and exam-board contexts using separate sessions.
- Require a clear explanation, a worked example and a quick comprehension check when appropriate.
- Test hint-first guided questions: the tutor waits for the learner's attempt before showing the solution.
- Check correction of misconceptions without shaming, unsupported certainty or claims of official marking.
- Verify the model distinguishes general teaching from facts that require official specification evidence.
- Verify citations link to retrieved sources and accurately support the nearby claim; say when evidence is absent.

### Safety and prompt injection
- Test benign questions, age-appropriate sensitive topics, harassment, requests for dangerous wrongdoing and attempts to obtain personal data.
- Test user prompt injection and hostile instructions embedded in retrieved documents.
- Retrieved documents must remain untrusted evidence, not instructions to the assistant.
- Verify input/output moderation and fail-closed behaviour where applicable; moderation is not a complete safeguarding system.
- Provide an adult-reviewed reporting/escalation route and clear learner guidance for seeking help.

### Privacy and account boundaries
- Verify no personal profile is sent unless the learner has opted in and only allow-listed fields are included.
- Switch between two synthetic accounts and confirm chat, profile, progress and exports never cross account boundaries.
- Confirm chat saving is opt-in, history is deletable, sign-out clears session data, and account deletion follows the documented retention policy.
- Verify uploaded files are type/size limited and are not retained unexpectedly.
- Inspect application logs and analytics for accidental prompt, profile or credential exposure.

## Full navigation and device QA
Test on at least one current Android phone and one laptop browser:
- Welcome, Dashboard, AI Teacher, Student Navigator, My learning profile
- Career pathways, Study planner, Research insights
- Global Knowledge Hub, Academic Profile Analyzer, Subject Catalogue
- Student feedback, Account & privacy, About EduBridge
- Sign-up, sign-in, sign-out, refresh, expired session and password/reset flows where configured
- Keyboard focus, screen-reader labels, touch target sizes, long content, empty states and error states
- Chat Compact/Balanced/Wide selection, reruns, message submission and browser navigation
- Global country search, indicator source links, latest observation years, missing data and API outage handling
- Research Lab learner insights while switching accounts and clearing session state

## World Bank data verification
- Confirm catalogue count and regions against the live World Bank country API.
- Confirm each selected indicator returns a value and year when available.
- Confirm missing observations are shown as unavailable, never as zero.
- Confirm chart labels include units and source links remain visible.
- Do not compare personal student progress with country-level indicators as though they measure the same thing.

## Student pilot gate
Do not invite students until all of the following are recorded:
1. CI passes on the release commit.
2. Adult supervisor approves provider terms, age eligibility, free-tier limits and no-billing safeguards.
3. Runtime checklist passes with synthetic accounts and no real student personal data.
4. Privacy notice, consent, deletion, incident response and adult escalation are reviewed.
5. Navigation, mobile/laptop, accessibility and account-isolation checks pass.
6. Any defects are fixed and retested.

A successful CI run or attractive interface is not proof of production readiness. If no hosted provider is both permitted for the intended users and genuinely $0, keep public generative tutoring disabled. Use an adult-managed local model for supervised evaluation only.
