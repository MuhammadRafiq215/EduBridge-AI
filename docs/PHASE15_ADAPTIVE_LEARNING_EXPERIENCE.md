# Phase 15 — Adaptive Learning Experience

## Product goal
Turn EduBridge from a set of separate learning tools into a repeatable learning loop: understand a topic, practise it, reflect on the attempt, and receive a transparent suggestion about what to revisit.

## Delivered in this phase
- **Guided Practice Studio** in Student Navigator.
- Learner chooses a subject, a specific topic, difficulty and practice style.
- When a provider is configured, the AI Teacher generates three age-appropriate questions with hints and can provide formative feedback on the learner's written attempt.
- Official specification records are retrieved for the chosen subject context where matching records exist; the UI shows those sources separately.
- When no provider is configured, the app offers an explicitly labelled offline recall/explain/apply scaffold. It does not pretend to generate subject-specific questions or mark answers.
- Practice reflection is added to temporary session progress by default. Signed-in learners can explicitly opt to save it to their private profile.
- A learner's self-reflection is not converted into a correctness score. The UI does not assign formal grades.
- A revision queue suggests review dates using transparent intervals: provisional/low progress = next day, developing = three days, stronger recent signals = seven days.
- The Welcome page now explains the Understand → Practise → Improve learning loop and connects it to the main workspaces.

## Progress and personalisation
Existing topic progress uses the latest self-reported confidence and optional practice records. The progress index is a planning signal only, not a grade, diagnosis or prediction. Practice reflection without independently marked questions remains provisional.

Revision intervals are deterministic heuristics, not a trained model or evidence that a learner will retain material. Learners can ignore or change the suggested schedule.

## Safety and privacy
- AI-generated practice and feedback use the existing provider adapter, including moderation on the official OpenAI endpoint.
- Input and generated content remain subject to the existing provider safeguards and age-appropriate tutor instructions.
- Practice answer text is processed in the current session and is not added to saved chat history by this feature.
- Topic reflections are temporary unless the signed-in learner explicitly chooses to save them.
- Never put provider credentials in source code or GitHub. Adult-managed provider configuration, required consent, privacy review and budget approval remain prerequisites for live hosted generation.

## Validation
GitHub Actions must pass compilation and the full unit-test suite. Manual checks remain required on mobile and desktop:
- Navigate from Welcome to AI Teacher and Student Navigator.
- Generate an AI practice set with a configured provider.
- Verify the offline scaffold appears honestly without a provider.
- Submit an answer and check formative feedback.
- Confirm topic reflection appears in progress and that optional profile saving works.
- Confirm revision dates and source links are displayed correctly.
