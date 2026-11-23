# Phase 27 — Career Discovery and Personalised Navigator

## Career Discovery Studio
- Expands the starter catalogue to 19 broad sectors, including engineering, digital technology and AI, health, natural sciences, agriculture and food systems, energy and environment, finance, law and policy, media, hospitality, manufacturing and robotics, cybersecurity, transport and logistics, education, sports science, public service and veterinary/animal sciences.
- Each sector includes an overview, preparation subject themes, degree directions, starter project ideas and selected learning resources.
- Adds free-text search across sector names, descriptions, degree names and project ideas.
- Adds subject filters so students can discover sectors connected to subjects they currently study or enjoy.
- Sector descriptions explicitly state that preparation themes are exploratory, not universal admissions requirements.
- Catalogue structure informed by Advance CTE's modern Career Clusters framework and College Board career cluster descriptions:
  - https://careertech.org/career-clusters/about-the-national-career-clusters-framework/
  - https://bigfuture.collegeboard.org/explore-careers/career-clusters

## Student Navigator
- Adds an interactive learning intent selector: understand a concept, practise questions, review a topic, or explore careers.
- Adds a time-available selector (10 minutes to one hour).
- Shows a matching next action and routes the learner to the relevant workspace.
- Retains the existing profile-based subject focus, saved topic records, adaptive priorities and session-only recent question context.
- Does not infer ability, predict grades or make admissions decisions.

## Testing
- Career catalogue coverage and completeness.
- Search by sector, degree and project text.
- Subject-based filtering and combined search/filter behaviour.
- Empty search returns the full catalogue.
- Full CI remains the merge gate.

## Scope and limitations
- Degree names are broad study directions, not a recommendation that every university offers them.
- Subject themes vary by country, curriculum and institution.
- Resources are starter links; learners should check current official programme and admission pages.
- AI Teacher generation remains separate from the Navigator. Public hosted generation must remain disabled until Cloudflare confirms in writing that the intended application for students aged 13–17 is permitted and the adult supervisor approves privacy, model licence, safety and budget controls.
- No API token or credential is stored in source control, Supabase tables or browser code.
