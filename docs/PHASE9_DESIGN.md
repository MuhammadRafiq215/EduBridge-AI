# Phase 9 — Learning experience and visual direction

## Design references

EduBridge uses product patterns as inspiration, not copied branding, illustrations or page layouts:

- **Khan Academy:** a learner home base that makes current work, progress and the next useful action easy to find. See the [student dashboard guide](https://support.khanacademy.org/hc/en-us/articles/46935588089997-How-do-I-use-the-student-dashboard-in-Khan-Academy) and [new classroom experience](https://blog.khanacademy.org/meet-the-new-khan-academy-classroom-experience/).
- **Duolingo:** consistent navigation, short clear actions, visible progress and friendly interaction details. See [how Duolingo refined its core tabs](https://blog.duolingo.com/core-tabs-redesign/).
- **Brilliant:** learning through clear explanations, hands-on problems, visualisations and immediate feedback. See [how Brilliant organises its courses](https://brilliant.org/help/courses-and-curriculum/what-subjects-does-brilliant-teach/).
- **Streamlit:** use supported theme configuration as the foundation and keep custom styling focused; avoid depending on fragile internal selectors where practical. See [Streamlit design best practices](https://docs.streamlit.io/develop/concepts/design/best-practices) and [theming](https://docs.streamlit.io/develop/concepts/configuration/theming).

## Phase 9 first delivery

- Added a dedicated Welcome workspace, separate from the signed-in Dashboard.
- Added three clear entry points: AI Teacher, Student Navigator and Learning Profile.
- Added a landing-page question box that carries a question into the full AI Teacher workspace.
- Added a persistent sidebar quick-question form so learners can open the AI Teacher from any workspace.
- Added responsive feature cards, clearer visual hierarchy, focus styling and reduced-motion handling.
- Kept the existing Dashboard, learning tools, source-coverage warnings and privacy controls intact.

## Design principles for the next iterations

1. Keep the next action obvious on every page.
2. Use progress visuals only when they represent real learner-entered or recorded evidence.
3. Keep AI chat one click away without forcing it open or covering learning content.
4. Use consistent colours, typography, spacing and button behaviour across workspaces.
5. Make interactive elements keyboard reachable, readable and responsive on narrow screens.
6. Prefer original EduBridge visual assets and simple illustrations over copying another product's mascot or identity.
7. Test the actual deployed app on desktop and mobile before calling a design complete.

## Not yet completed

This first delivery is a foundation, not a claim that the whole site is finished. A deeper workspace-by-workspace redesign, accessibility review, real-device testing, live local-model testing and persistent-database verification remain separate tasks.
