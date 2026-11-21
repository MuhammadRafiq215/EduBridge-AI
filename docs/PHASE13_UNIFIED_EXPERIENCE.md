# Phase 13 — Unified navigation, Welcome and offline AI Teacher

## What the screenshots revealed
The repository uses Streamlit's legacy `pages/` directory for Global Knowledge Hub, Academic Profile Analyzer and Subject Catalogue, while `app.py` renders a separate custom workspace radio. Streamlit therefore displays two independent navigation menus. On those legacy pages, the custom app sidebar is not executed.

## Navigation changes
- Hide the automatically generated legacy sidebar menu using `client.showSidebarNavigation = false`.
- Add `src/navigation.py` as a shared branded sidebar for all three standalone tool pages.
- Show the same student workspaces and tool destinations from every page.
- Add links to the three tools inside the main app's existing sidebar.
- Preserve the existing workspace selector and route workspace buttons back through Streamlit's page switcher.

## Welcome experience
- Add a dedicated Welcome workspace as the first-run default for new sessions.
- Provide clear entry points into AI Teacher, Student Navigator, learner profile, career pathways, study planner and research insights.
- Keep the Dashboard available as a separate workspace.

## AI Teacher offline helper
- When no hosted/local model is configured, show a clearly labelled offline source helper.
- Accept a question and search reviewed specification records and subject catalogue entries.
- Display the retrieved notes, record status, limits and official source links.
- Clearly distinguish retrieval from generated tutoring. No provider is impersonated and no external API call is made.
- Full generative tutoring still requires a separately configured provider.

## Design references and principles
The interface uses an original EduBridge visual system. Design research drew on:
- Khan Academy's published 2026 work on semantic colour systems and accessibility: https://blog.khanacademy.org/how-we-rebuilt-khan-academys-color-system-from-the-ground-up/
- Duolingo's 2025 core-tabs redesign, which emphasises consistent headers, typography, spacing and coherent navigation: https://blog.duolingo.com/core-tabs-redesign/
- Streamlit's recommended `st.Page` / `st.navigation` multipage architecture: https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation

The implementation borrows general principles only; it does not copy third-party logos, illustrations, text or proprietary screens.

## Validation and release gates
- GitHub Actions compilation and unit tests must pass.
- Verify the live app on mobile and desktop after deployment.
- Confirm all ten workspace choices and all three tool pages remain reachable.
- Test offline retrieval against known source examples and a no-match query.
- Live model generation is not enabled by this phase. It remains subject to adult account ownership, provider terms, privacy review, safeguarding and budget approval.
