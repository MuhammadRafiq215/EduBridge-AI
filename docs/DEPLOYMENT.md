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

The app also exposes Phase 3, Phase 4 and Phase 5 in Streamlit's multipage navigation. The page scripts are in `pages/`; Phase 5 uses `phase5.py` and the SHAP dependency listed in `requirements.txt`.
7. Open advanced settings and choose **Python 3.12**.
8. Select **Deploy** and wait for package installation and app startup.
9. When Streamlit displays the app, copy the exact URL shown in the app workspace. That is the deployed address to share.

## Choose an app URL

Streamlit may let you choose an available app subdomain during setup or app settings. A suitable name to try is:

`edubridge-ai-rafique`

The final address is assigned by Streamlit and may include the account/workspace portion. Availability is not guaranteed. The text `RAFIQUE@2048` is not a valid Streamlit subdomain because app URLs do not use an @ sign. Do not use a password or secret as a public URL.

A deployed website is not guaranteed to appear immediately in Google or other search engines. Share the exact Streamlit URL directly while search indexing catches up.

## First launch

1. Open the deployed app.
2. In the sidebar, select **Run / refresh experiment**.
3. Wait while the app downloads the official UCI archive and runs cross-validation and held-out evaluation.
4. Review the Research Overview, Model Lab, Evaluation and Responsible AI pages.

The first research experiment can take a few minutes. The hosted app needs outbound internet access to retrieve the UCI dataset. Learner profiles are session-based; persistent registration and sign-in are not enabled until an authentication provider and database are configured.

## Updating the website

When code is pushed to the connected GitHub branch, Streamlit Community Cloud normally detects the update and rebuilds/restarts the app. Check the app's **Manage app** page and logs if the update fails.

## Troubleshooting

- **Repository missing:** confirm that you signed into the correct GitHub account and authorized Streamlit for this private repository.
- **Dependency installation error:** open the Streamlit app logs and check the Python version and `requirements.txt`.
- **App starts but shows no metrics:** select **Run / refresh experiment** in the sidebar.
- **UCI download error:** check the app logs and retry later; the dataset is downloaded at runtime.
- **App URL unavailable:** choose another available subdomain in Streamlit's app settings.

## Security and research safeguards

- Do not add passwords, API keys or private student data to GitHub.
- Do not place credentials in source code or README files.
- Do not use the prototype to make decisions about individual students.
- The source dataset is from Portuguese schools and is not validated for Pakistan.
