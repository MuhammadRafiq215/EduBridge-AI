# Phase 11 — EduBridge visual identity

## Goal
Give the existing Streamlit application a consistent, modern visual system while preserving every existing workspace and interaction.

## Design direction
- **Midnight indigo** for the navigation shell and strong brand moments.
- **Violet** for primary actions, active navigation and learning highlights.
- **Teal** for progress accents and secondary emphasis.
- **Soft coral and lime** as restrained supporting accents.
- **Warm, near-white surfaces** with subtle gradients, clear borders and generous spacing.
- **DM Sans / Space Grotesk** typography already used by the application.

## Implementation
- Shared styling is isolated in `src/visual_design.py`.
- `apply_visual_identity()` is called after the existing page styles so the design system can consistently refine the app.
- `render_site_footer()` adds a responsive footer with links to the source repository and live application.
- Existing page routing, learner data, profile sharing defaults, AI provider settings, chat history and database logic are unchanged.

## Accessibility and responsive behaviour
- Clear focus outlines and readable text contrast are retained.
- Hover movement is subtle and disabled when the user requests reduced motion.
- Layout spacing and footer navigation adapt to narrower screens.
- No JavaScript, third-party tracking, credentials or new paid services are introduced.

## Verification checklist
- [ ] GitHub Actions compile and unit tests pass.
- [ ] Inspect Welcome, Dashboard, AI Teacher, Student Navigator, Profile, Career Pathways, Study Planner, Research Insights, Feedback, Account & Privacy and About pages at desktop and mobile widths.
- [ ] Check keyboard focus, reduced-motion mode, long labels and empty states.
- [ ] Confirm Supabase sign-in, profile storage, chat history and local AI runtime remain unchanged.
- [ ] Review the visual result in the deployed app before merging.

## Colour tokens
| Role | Colour |
| --- | --- |
| Midnight | `#14213B` |
| Indigo | `#343B83` |
| Violet | `#5B4DE8` |
| Teal | `#12A6A6` |
| Coral | `#F29A78` |
| Lime | `#D4F06A` |
| Canvas | `#F5F7FC` |
| Text | `#17233D` |

The colour system is a design layer only. It does not change the meaning of student progress, assessment data or AI outputs.
