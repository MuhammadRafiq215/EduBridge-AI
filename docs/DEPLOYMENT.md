# Deploy EduBridge AI on Streamlit Community Cloud

This guide deploys the Streamlit dashboard in `app.py`. The GitHub repository stores the source code; Streamlit Community Cloud hosts and runs the website.

## Before you begin

- A GitHub account with access to `MuhammadRafiq215/EduBridge-AI`.
- A Streamlit Community Cloud account.
- Permission to authorize Streamlit to read the repository.
- The repository's default branch is `main`.

**Repository visibility:** GitHub currently reports this repository as public. Anyone can read its code and commit history. Never commit passwords, API keys, private student records or personal documents.

## Deploy from a phone or computer

1. Open [https://share.streamlit.io/](https://share.streamlit.io/).
2. Sign in with GitHub.
3. If asked, authorize Streamlit Community Cloud to access `MuhammadRafiq215/EduBridge-AI`. If it is not listed, review the GitHub App/repository access settings for Streamlit and grant access to this repository.
4. Select **Create app**.
5. Choose the GitHub repository deployment option.
6. Enter:
   - **Repository:** `MuhammadRafiq215/EduBridge-AI`
   - **Branch:** `main`
   - **Main file path:** `app.py` (the main dashboard)

7. Open advanced settings and choose **Python 3.12**.
8. Select **Deploy** and wait for package installation and app startup.
9. When Streamlit displays the app, copy the exact URL shown in the app workspace. That is the deployed address to share.

## Configure Supabase accounts and profile storage

The app uses Supabase Auth and PostgreSQL for genuine student accounts and persistent profiles.

1. Create a Supabase project at https://supabase.com/dashboard.
2. Open the project's SQL Editor and run the complete contents of supabase/schema.sql. This creates student_profiles and enables row-level security policies that restrict each row to its authenticated owner.\n3. To enable the Student feedback workspace, run supabase/feedback_schema.sql as a separate SQL script. It creates an isolated feedback table with row-level security; visitors can submit but cannot read submissions. This does not modify student_profiles. The project owner can review submissions in the SQL Editor.
4. In Supabase, open Project Settings → API (or API Keys). Copy the Project URL and publishable key (or legacy anon key). Do not use the service_role/secret key.
5. In Streamlit Community Cloud, open the app's Manage app → Settings → Secrets and add:

~~~toml
[supabase]
url = "https://YOUR-PROJECT.supabase.co"
anon_key = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
~~~

5. In Supabase Authentication settings, configure email confirmation and the redirect/site URL for the exact Streamlit app URL. Test account creation, email verification, sign-in, profile save, sign-out and sign-in again.
7. Keep row-level security enabled on student_profiles. Never disable RLS and never put a service-role key in GitHub or Streamlit secrets.

Until the Supabase project and Streamlit secrets are configured, public learning and research pages can load, but account and persistent-profile features will not work. A profile is persisted only after successful sign-in and database setup.

### Supabase confirmation emails

Supabase's built-in email sender is intended for evaluation, not general public registration. Its current hosted-project restrictions include delivery only to authorised organisation-team addresses and a low project-wide sending limit (currently two emails per hour). A successful sign-up API response with no session means email confirmation is required; it does not prove that a message reached the inbox.

For public testing or production, the project owner should configure a supported custom SMTP provider in Supabase Authentication → SMTP Settings. The provider account and sending domain must be eligible under that provider's terms. Keep SMTP credentials in Supabase's SMTP settings only; never place them in GitHub, application source code, or Streamlit secrets. Check Supabase Authentication → Logs and the SMTP provider's delivery logs when messages are not received. Keep email confirmation enabled.

If a message is missing, check Spam/Promotions, verify the recipient address, inspect Auth logs, and respect the email rate limit before requesting another message. The app's resend action only works when an initial signup confirmation exists.

References:
- [Supabase custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp)
- [Supabase troubleshooting: not receiving Auth emails](https://supabase.com/kb/troubleshooting/not-receiving-auth-emails-from-the-supabase-project-OFSNzw)
- [Supabase Python: resend signup confirmation](https://supabase.com/docs/reference/python/auth-resend)

## Choose an app URL

Streamlit may let you choose an available app subdomain during setup or app settings. A suitable name to try is:

`edubridge-ai-rafique`

The final address is assigned by Streamlit and may include the account/workspace portion. Availability is not guaranteed. The text `RAFIQUE@2048` is not a valid Streamlit subdomain because app URLs do not use an @ sign. Do not use a password or secret as a public URL.

A deployed website is not guaranteed to appear immediately in Google or other search engines. Share the exact Streamlit URL directly while search indexing catches up.

## First launch

1. Open the deployed app and confirm the Dashboard loads.
2. Open Account & privacy and test sign-up and email verification.
3. Sign in, create a learning profile, save it, then refresh and sign in again to verify persistence.
4. Open Research insights to run the UCI benchmark and inspect the model comparison.

The first research experiment can take a few minutes. The hosted app needs outbound internet access to retrieve the UCI dataset. Student profiles are stored persistently through Supabase after the SQL schema and Streamlit secrets are configured.

## Updating the website

When code is pushed to the connected GitHub branch, Streamlit Community Cloud normally detects the update and rebuilds/restarts the app. Check the app's **Manage app** page and logs if the update fails.

## Troubleshooting

- **Repository missing:** confirm that you signed into the correct GitHub account and authorized Streamlit for this repository.
- **Dependency installation error:** open the Streamlit app logs and check the Python version and `requirements.txt`.
- **Account features unavailable:** confirm Streamlit secrets use the exact supabase URL and anon_key names, and that supabase/schema.sql was executed.
- **UCI download error:** the app searches the official UCI archive and nested ZIP files, then retries the official legacy archive. If UCI is temporarily unavailable, retry later and inspect Streamlit logs.
- **Profile export:** the learner-facing download is a printable PDF. JSON remains available in the optional data-portability expander.\n- **Student feedback:** run supabase/feedback_schema.sql in the SQL Editor. The feedback form does not ask for names or contact details; review entries in the SQL Editor and remove them when no longer needed. Public insert-only access is suitable for a small pilot, not an unmoderated high-traffic public launch.
- **App URL unavailable:** choose another available subdomain in Streamlit's app settings.

## Security and research safeguards

- Do not add passwords, API keys or private student data to GitHub.
- Never use the Supabase service-role key in the Streamlit app.
- Keep row-level security enabled and test that two accounts cannot read one another's profiles.\n- The student_feedback table intentionally has no public SELECT policy. Only the project owner should review its entries in the Supabase SQL Editor.
- Do not place credentials in source code or README files.
- Do not use the prototype to make decisions about individual students.
- The source dataset is from Portuguese schools and is not validated for Pakistan.
