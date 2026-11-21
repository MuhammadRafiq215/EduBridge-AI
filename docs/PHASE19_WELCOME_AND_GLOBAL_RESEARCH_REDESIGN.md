# Phase 19 — Welcome Experience & Global Research Explorer

## What changed
- Replaced the three narrow Welcome-page columns with a responsive CSS grid. Cards reflow from three columns on desktop to two at tablet widths and one on small phones.
- Added explicit actions for Understand, Practise and Improve destinations.
- Rebuilt Research Lab around a country-comparison explorer using the World Bank API.
- Removed the hard-coded Pakistan literacy and numeracy figures from the student-facing research page.
- Moved the Portuguese student-performance ML experiment into a separate tab and kept its population and limitations visible.

## Global indicator design
The explorer currently supports:
- Adult literacy (ages 15+)
- Primary school gross enrolment
- Secondary school gross enrolment
- Tertiary education gross enrolment

Country observations are retrieved from the World Bank API at runtime and cached for 24 hours. The interface displays the observation year and explicitly identifies unavailable values. It does not calculate a student ranking, compare a learner's marks with national literacy, or infer an individual outcome from country-level data.

## Data interpretation safeguards
- The latest available observation can be from a different year for each country.
- Gross enrolment ratios can exceed 100%; they are not completion rates.
- Adult literacy is a population-level indicator, not an examination result.
- Country comparisons are descriptive context, not a league table.
- World Bank data may be unavailable temporarily; the interface must show that honestly.

## Validation
Automated CI checks Python compilation and the repository test suite. Manual verification is still required at phone and laptop widths, especially the Welcome cards and the country-comparison controls. Verify the deployed Streamlit app separately after merge.

## Source
- World Bank indicator catalogue: https://data.worldbank.org/indicator
- World Bank API documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- UCI Student Performance dataset: https://archive.ics.uci.edu/dataset/320/student+performance
