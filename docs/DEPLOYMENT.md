# Deploy EduBridge AI on Streamlit Community Cloud

The repository is structured for Streamlit Community Cloud: the entrypoint `app.py`, root-level `requirements.txt`, and optional Streamlit configuration at `.streamlit/config.toml` are in the expected locations.

## One-time deployment steps

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using the GitHub account that owns this public repository.
2. Select **Create app**.
3. Choose **Deploy a public app from GitHub** (or the equivalent option shown in your workspace).
4. Set repository to `MuhammadRafiq215/EduBridge-AI`.
5. Set branch to `main`.
6. Set main file path to `app.py`.
7. In Advanced settings, select Python 3.12.
8. Deploy and wait for dependency installation and app startup.

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## First launch

The dashboard initially displays instructions because experiment outputs are generated at runtime. In the sidebar, select **Run / refresh experiment**. The app downloads the UCI Student Performance archive, trains and evaluates the baseline models, and saves generated files in the app's local runtime.

The first experiment may take a few minutes. If the UCI download is unavailable, retry later and inspect the app logs in the Streamlit workspace.

## Important hosting note

A GitHub repository is source code storage; it does not itself run a public website. A Streamlit Community Cloud deployment must be created and authorized by the repository owner. Once deployed, pushes to the connected GitHub repository are reflected by Community Cloud.

Do not add passwords, API keys, or private student information to this repository.
