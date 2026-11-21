# Phase 13 — Responsive workspace navigation

## Problem addressed
On compact/mobile screens, Streamlit's sidebar can close after a workspace is selected. This can make the other sidebar destinations appear to have disappeared, even though the workspace selector still contains them.

## Change
- Preserve the existing full sidebar selector and all of its destinations.
- Add a compact **Quick access** row below the EduBridge brand strip on every workspace.
- Keep Dashboard, AI Teacher and Student Navigator reachable without reopening the sidebar.
- Route button clicks through the existing pending-workspace mechanism so navigation state is updated before the sidebar radio widget is created.
- Use the existing EduBridge visual language and responsive layout rules.

## Design rationale
The change applies progressive disclosure: the three most-used learner destinations stay prominent, while secondary destinations remain in the complete sidebar. It avoids hiding navigation with fragile CSS selectors and avoids a risky full router migration in this incremental release.

## Validation
GitHub Actions runs compilation and unit tests on this branch. A successful CI run does not replace desktop and mobile browser checks. Confirm the public Streamlit deployment after merging the reviewed pull request.

## AI Teacher connection status
This phase does not add an API key or enable paid model generation. The AI Teacher requires an adult-managed provider configuration in Streamlit Secrets. A local model endpoint on a student's laptop is not reachable from Streamlit Community Cloud.
