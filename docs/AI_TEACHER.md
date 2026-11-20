# AI Teacher and knowledge-base setup

EduBridge AI includes a modular AI Teacher workspace. The interface is separate from
the model provider, so a compatible provider can be replaced without rewriting the
Streamlit page.

## Configure a provider

The first adapter supports providers that implement the OpenAI-compatible Chat
Completions API, including text and image input. Add credentials only to the
Streamlit app's **Manage app → Settings → Secrets** panel; never commit them to Git.

~~~toml
[ai]
base_url = "https://api.openai.com/v1"
api_key = "YOUR_PROVIDER_API_KEY"
model = "YOUR_TEXT_AND_VISION_CAPABLE_MODEL"
~~~

Use a provider and model that explicitly support image input if you want screenshot
interpretation. Provider pricing, age requirements, data handling and geographic
availability vary; the project owner must review the provider's current terms and
privacy policy before enabling it. Do not bypass age or account eligibility rules.
Never share provider keys in chat, screenshots, source code or GitHub issues.

## Trusted examination knowledge base

EduBridge uses a retrieval layer rather than claiming that a general model has been
trained on every qualification. At question time it searches locally stored,
human-reviewed official-source records and passes relevant excerpts to the tutor.
The tutor is instructed to cite retrieved records using their `[KB:source_id]`
identifier and not to extend rules beyond the qualification or year covered by a
source.

The retrieval engine is in `src/knowledge_base.py`. The data format and review
checklist are in `data/knowledge_base/README.md`.

### Current starter coverage

The initial source set includes Cambridge IGCSE qualification and threshold guidance,
Cambridge recognition in Pakistan, Pearson Edexcel International GCSE, an FBISE grading
notification, a Türkiye MEB upper-secondary assessment overview, and a WAEC WASSCE
subject e-Learning page. These are a small starting collection, not full board coverage.
Subject specifications, exam series, local rules and current notices must be added
and reviewed individually.

### Add examination sources

Add one JSON object per line to `data/knowledge_base/documents.jsonl`. Required
metadata includes a stable source ID, title, issuer, official HTTPS URL, qualification,
country, awarding body, topic, short factual summary, review date, status and an
explicit `is_official` boolean.

Only records with both `status: "verified"` and `is_official: true` are eligible for
retrieval. Draft, unreviewed and archived records are excluded. Prefer official
syllabuses, assessment specifications, grading notices, qualification-framework
documents and government education guidance. Check the exact qualification, version,
year and jurisdiction. Do not commit full copyrighted syllabuses, paid textbooks,
exam papers or other materials unless redistribution is clearly permitted; use
short paraphrased summaries with source links.

The qualification, country and awarding-body fields in the AI Teacher can be entered
freely when a learner's system is not listed. This makes the learner's context
flexible; it does **not** make that qualification's rules verified automatically.
If no matching official source exists, the tutor is instructed to say so, give only
clearly labelled general guidance where appropriate, and ask for the official
awarding body or source.

## What this version does

- Uses a small allow-list of education fields from the saved learner profile when
  the learner opts in.
- Allows a learner to enter an unlisted qualification, country and awarding body.
- Retrieves relevant verified official records and displays source links.
- Rejects malformed records and excludes unreviewed/non-official records.
- Accepts PNG, JPEG and WebP images up to 5 MB.
- Keeps chat history in Streamlit session state only; it is not written to Supabase.
- Uses a provider adapter (ChatProvider) so another provider can be implemented.

## Current limitations

- This is a provider-connected tutor prototype, not a fine-tuned model.
- The AI provider is not configured by default. The app does not generate pretend
  answers when no provider is available.
- The current source set is deliberately small and needs systematic expansion.
- Retrieval currently uses lightweight lexical matching. A vector/semantic search
  layer can be added after the source collection and evaluation set grow.
- The configured model must support image input for screenshot interpretation.
- There are no global grade percentiles or rankings. Those require representative,
  qualification-specific, year-specific datasets and careful validation.
- Chat history is temporary and will be cleared when the browser session ends or
  the learner clears it.
