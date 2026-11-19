# Deploy EduBridge AI on Streamlit Community Cloud

This guide deploys the Streamlit dashboard in `app.py`. The GitHub repository stores the source code; Streamlit Community Cloud hosts and runs the website.

## Before you begin

- A GitHub account with access to `MuhammadRafiq215/EduBridge-AI`.
- A Streamlit Community Cloud account.
- Permission to authorize Streamlit to read the repository.
- The repository's default branch is `main`.

**Repository visibility:** the repository is currently private. Streamlit Community Cloud can be authorized to access a private repository; public visibility is not technically required. If you still want the code public, change it separately in GitHub under **Settings → General → Danger Zone → Change repository visibility → Make public**. Review the entire repository first: public means anyone can read and copy its code and history. Never commit passwords, tokens, private records or personal documents.

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
2. Open the project's SQL Editor and run the complete contents of supabase/schema.sql. This creates student_profiles and enables row-level security policies that restrict each row to its authenticated owner.
3. In Supabase, open Project Settings → API (or API Keys). Copy the Project URL and publishable key (or legacy anon key). Do not use the service_role/secret key.
4. In Streamlit Community Cloud, open the app's Manage app → Settings → Secrets and add:

~~~toml
[supabase]
url = "https://YOUR-PROJECT.supabase.co"
anon_key = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
~~~

5. In Supabase Authentication settings, configure email confirmation and the redirect/site URL for the exact Streamlit app URL. Test account creation, email verification, sign-in, password reset, profile save, sign-out and sign-in again.
6. Keep row-level security enabled on student_profiles. Never disable RLS and never put a service-role key in GitHub or Streamlit secrets.

Until the Supabase project and Streamlit secrets are configured, public learning and research pages can load, but account and persistent-profile features will not work. A profile is persisted only after successful sign-in and database setup.

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
- **UCI download error:** check the app logs and retry later; the dataset is downloaded at runtime.
- **App URL unavailable:** choose another available subdomain in Streamlit's app settings.

## Security and research safeguards

- Do not add passwords, API keys or private student data to GitHub.
- Never use the Supabase service-role key in the Streamlit app.
- Keep row-level security enabled and test that two accounts cannot read one another's profiles.
- Do not place credentials in source code or README files.
- Do not use the prototype to make decisions about individual students.
- The source dataset is from Portuguese schools and is not validated for Pakistan.
