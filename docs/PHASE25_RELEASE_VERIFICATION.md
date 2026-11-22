# Phase 25 — Quality, accessibility and release verification

## Product/design direction
Phase 25 refines the existing EduBridge identity rather than copying another product. The visual system uses a deep ink foundation with cobalt, teal, coral and warm-gold accents, layered light surfaces, consistent cards, readable input controls and reduced-motion support.

The implementation follows current Streamlit guidance to prefer native components and theme settings where practical, and uses responsive CSS only for shared visual surfaces. See:
- https://docs.streamlit.io/develop/concepts/design/best-practices
- https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders

Accessibility checks are informed by WCAG 2.2:
- Text contrast target: 4.5:1 for normal text.
- Reflow at 320 CSS pixels without loss of information or functionality.
- Visible keyboard focus and non-colour-only status cues.
- Pointer targets at least 24 by 24 CSS pixels where the criterion applies.
- Respect reduced-motion preferences.

Reference: https://www.w3.org/TR/WCAG22/

## Code changes
- Refines global colour tokens and adds a richer cobalt/teal/coral accent system.
- Improves mobile spacing and metric/card wrapping at narrow widths.
- Adds stronger focus indicators, scroll margins and reduced-motion overrides.
- Aligns Streamlit's native theme with the shared visual tokens.
- Clears credentials, learner profile, chat, topic progress and guided-practice state on sign-out, preventing stale learner-owned content from remaining in a shared browser session.
- Adds a regression test for sign-out cleanup.

## Release checklist — must be performed against the deployed app
1. Visual: Welcome, Dashboard, Navigator, AI Teacher, Guided Practice, Career, Planner, Research and Explore Tools.
2. Responsive: desktop, tablet, 390px phone and 320px narrow viewport; no clipped controls or horizontal page scrolling.
3. Subject catalogue: search by typing, select catalogue items, custom subject entry, profile subjects included.
4. Topic records: validate empty topic, save to session, save to signed-in profile, reload, edit/revisit, and check counts.
5. Account isolation: two synthetic test accounts; sign out A, sign in B, verify no profile/chat/topic/practice state from A appears.
6. Guided Practice: offline scaffold clearly labelled; configured provider success and failure; subject/topic/difficulty/format; attempt feedback; no false formal grading.
7. AI Teacher: no-provider state, local model availability, timeout/network/auth/quota errors, prompt injection, safety-screening failure, source citation accuracy and uncertainty.
8. Privacy: history off by default, explicit opt-in, delete history, profile deletion, session cleanup, RLS policies and no secrets in browser-visible output/logs.
9. Navigation: every sidebar item, quick action, page link, back/forward and sign-out.
10. Accessibility: keyboard-only navigation, visible focus, 200% zoom, text contrast, labels, screen reader smoke test, reduced motion.

## Evidence boundary
Automated unit tests and CI do not prove live deployment, device rendering, provider availability, Supabase RLS configuration or real two-account isolation. These require a supervised live test with synthetic accounts and screenshots/log evidence. Do not mark the release complete until those checks are recorded.
