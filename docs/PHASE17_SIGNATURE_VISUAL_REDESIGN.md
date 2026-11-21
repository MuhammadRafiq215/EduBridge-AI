# Phase 17 — EduBridge Signature Visual Redesign

## Design direction
An original "learning studio" identity: editorial typography, calm paper surfaces, deep ink navigation, electric blue/cyan interaction accents and a small lime signal colour. The aim is to feel like a focused modern product rather than a generic school portal.

## References studied
- Linear: restrained workspace hierarchy and low-noise navigation.
- Vercel: consistent component states, typography and precise spacing.
- Khan Academy: approachable learning-oriented colour and information hierarchy.
- Vercel Web Interface Guidelines: inline help, explicit empty/error states, redundant status cues and no dead ends.

These references informed principles only. EduBridge uses its own palette, layout rules and brand identity; it does not reproduce another product's screens or assets.

## Changes
- Added `src/visual_design.py` as a shared responsive design system.
- Applied the same visual identity to the main app and standalone knowledge, profile-analysis and subject-catalogue pages.
- Suppressed Streamlit's generated duplicate multipage sidebar list so EduBridge's own navigation remains the single source of navigation.
- Kept all 11 student workspaces and the three Explore Tools links in the app-owned navigation.
- Improved sidebar scrolling, mobile spacing, active navigation, cards, metrics, forms, chat messages, chat input and focus states.
- Added reduced-motion handling and high-contrast interaction states.

## AI Teacher
The redesign changes presentation only. The existing AI Teacher still requires a configured model provider for generated tutoring. Without one, the app uses its explicitly labelled offline source helper. The interface must never claim a model is connected when it is not.

## Verification
- GitHub Actions compile and unit tests.
- Verify all 11 workspaces and three Explore Tools links on the main app and standalone pages.
- Check narrow mobile, tablet and desktop layouts.
- Confirm sidebar scrolling and active-state visibility.
- Test AI Teacher in both no-provider and authorised-provider states.
- Check empty profile, populated profile, errors and keyboard focus.

A passing CI run does not replace visual browser testing. The deployed Streamlit app must be checked after merge.
