# AI Teacher runtime setup

## Supported runtime modes

EduBridge supports two explicitly configured modes:

1. **Local model server** — sends prompts to a local Ollama-compatible service on the same computer as Streamlit. No hosted AI account or API key is required for this mode.
2. **Hosted OpenAI-compatible provider** — requires an API key, model name, provider endpoint and confirmation that the account, deployment and data handling comply with the provider's terms.

EduBridge does not ask learners for a date of birth or age in its student profile. External model providers and hosting platforms can still have their own terms. Do not bypass account requirements or use another person's credentials without permission.

## Local mode on Windows

1. Install the local model runtime from the [official Ollama Windows download page](https://ollama.com/download/windows).
2. Start the runtime.
3. In PowerShell, use the runtime's documented model command to install and start a model. Use a model that your computer can reasonably run; memory and speed depend on the model and hardware.
4. Check the installed model name with `ollama list`.
5. Add the following to the local Streamlit secrets file at `.streamlit/secrets.toml` (create this file locally; it is ignored by Git):

```toml
[ai]
provider = "local"
model = "YOUR_INSTALLED_MODEL_NAME"
base_url = "http://127.0.0.1:11434"
timeout = 120
supports_vision = false
```

6. Start EduBridge locally with `streamlit run app.py`.
7. Open AI Teacher and ask a short test question.

The local adapter calls the native `/api/chat` endpoint with streaming disabled. It sends no Authorization header and only accepts loopback addresses (`localhost`, `127.0.0.1`, or `::1`). Image upload remains hidden unless `supports_vision = true` is explicitly set and the installed model supports images.

## Recommended first model for a 16 GB Windows laptop

For a computer showing **15.8 GB total RAM** and about **9.5 GB available at the time of checking**, begin by testing **Qwen 3.5 4B**. The official Ollama library lists the `qwen3.5:4b` model at approximately 3.3–4.0 GB and identifies text and image input support. This is a reasonable first trial, not a guarantee of speed: CPU/GPU, current memory pressure, context length and other running applications all affect performance.

After installing Ollama from the official Windows installer, open PowerShell and run:

```powershell
ollama run qwen3.5:4b
```

The first run downloads the model. Wait for its prompt, enter a short test question, then use `/bye` to exit the model chat. Check the installed model name with:

```powershell
ollama list
```

Use the exact installed model tag in the local EduBridge secrets file:

```toml
[ai]
provider = "local"
model = "qwen3.5:4b"
base_url = "http://127.0.0.1:11434"
timeout = 180
supports_vision = true
```

Qwen 3.5 4B supports image input in Ollama's model library, so vision can be enabled after confirming the installed model runs successfully. If the laptop becomes sluggish or Windows reports low available memory, stop the model and try the smaller `qwen3.5:2b` tag instead. Do not run multiple large models at once. Start with short prompts and close unnecessary applications.

Official model pages:
- [Qwen 3.5 4B in the Ollama library](https://ollama.com/library/qwen3.5:4b)
- [Qwen 3.5 model tags and published sizes](https://ollama.com/library/qwen3.5/tags)

## Important deployment distinction

A Streamlit Community Cloud app runs on Streamlit's server. Its `localhost` is the cloud server, not your Windows laptop. Therefore, the local mode above is for running EduBridge and the local model runtime on the same computer. It does not make the deployed public app reach your laptop.

For a hosted deployment, configure an eligible hosted provider through Streamlit Secrets only after its terms, account eligibility, privacy, retention and pricing are confirmed. Example shape:

```toml
[ai]
provider = "openai_compatible"
api_key = "YOUR_PROVIDER_KEY"
model = "YOUR_PROVIDER_MODEL"
base_url = "https://YOUR_PROVIDER_ENDPOINT/v1"
timeout = 60
supports_vision = false
```

Never commit secrets to GitHub, place them in source code, or paste them into the AI Teacher chat. Do not use a service-role database key in the application.

## Learner privacy

- EduBridge's student profile does not request age or date of birth.
- Saved profile context is sent to the model only after the learner actively enables the profile-sharing checkbox.
- Only the latest 12 text messages are sent as conversation context.
- Screenshots are sent only when image support is enabled; screenshots are not saved in EduBridge's chat-history table.
- Permanent chat history is off by default and requires sign-in plus explicit opt-in.
- To enable persistent history, apply `supabase/chat_history_schema.sql` in the correct Supabase project. The migration is not run automatically.
- Learners can delete their saved chat history from the AI Teacher workspace.

## Current limitations

- A local model's answer quality and speed depend on the chosen model and the computer's hardware.
- The local provider is not a cloud-hosted service and cannot serve the Streamlit Cloud deployment through the laptop's loopback address.
- A hosted provider is not active unless valid settings are supplied in Streamlit Secrets.
- Vision support is model-dependent and must be explicitly enabled.
- Retrieved official sources help ground exam-board answers but do not guarantee complete global syllabus coverage or perfect answers.

## Technical references

- [Ollama Windows download](https://ollama.com/download/windows)
- [Ollama API overview](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ollama chat endpoint](https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion)
