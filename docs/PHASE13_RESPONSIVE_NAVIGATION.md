# Phase 13 — Responsive and unified navigation

The mobile screenshots showed two separate Streamlit navigation systems: the custom workspace selector in `app.py` and the automatically generated menu from the legacy `pages/` directory.

## Implemented changes
- Hide Streamlit's legacy auto-generated sidebar navigation.
- Keep the complete custom workspace selector in the main EduBridge app.
- Add the three knowledge tools to the main sidebar.
- Add a shared branded sidebar to Global Knowledge Hub, Academic Profile Analyzer and Subject Catalogue.
- Make every workspace and tool reachable from all three standalone pages.
- Keep the compact Dashboard / AI Teacher / Student Navigator quick-access row on the main workspace.
- Add a first-run Welcome workspace with clear entry points to the student tools.

## AI Teacher fallback
When no live model is configured, AI Teacher now offers an explicitly labelled offline source helper. It searches reviewed EduBridge specification records and subject catalogue entries and displays source status, notes, limits and official links. This is retrieval, not generative AI. It does not pretend that a live model is online.

## Design
The implementation uses an original EduBridge visual identity: midnight-indigo navigation, teal-violet action accents, a lime highlight, clear typography, rounded but restrained cards, consistent hierarchy and mobile-friendly spacing. It borrows general design principles from published learning-product design articles, not third-party branding or proprietary screens.

## Release checks
- GitHub Actions compilation and unit tests must pass.
- Test workspace switching from each of the three knowledge pages.
- Test the main Welcome page and all tool links on mobile and desktop.
- Test the offline source helper with both matching and no-match questions.
- Live generative tutoring remains disabled until a permitted provider, adult-managed credentials, safeguarding and privacy review, and an approved budget are in place.
