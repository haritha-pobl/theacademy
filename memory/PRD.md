# PRD — The Academy Website

## Original Problem Statement
"Build a website using the html file I've uploaded." — User uploaded `the-academy-ai-upskill-site.html`, a complete self-contained multi-page site for "The Academy" (Full-Stack career programs, Coimbatore).

## Architecture
- The uploaded HTML file (self-contained: inline CSS/JS, embedded images, Google Fonts CDN) is served directly as the site's main page at `/app/frontend/public/index.html`.
- Original React template backed up at `/app/frontend/public/index-react-backup.html`.
- `/app/frontend/src/index.js` guards against missing `#root` so the injected React bundle stays inert.
- Backend (FastAPI on :8001, /api prefix) and MongoDB remain available but unused by the static site.

## User Personas
- Prospective students in Coimbatore exploring Full-Stack career programs (Marketing, HR, Accounting tracks)
- Visitors checking batch availability and applying/reserving seats

## Core Requirements
- Serve the uploaded HTML exactly as designed, at the site root URL
- Preserve all in-file navigation (Home, Why The Academy, Programs, Batches, Landing tabs) and CTAs

## Implemented
- 2026-08-30: Uploaded HTML deployed as the live site root; verified hero, all 5 tabs, "See Open Batches" CTA, batch cards, and footer render correctly with zero console errors.

## Backlog / Next Tasks
- P0: None — site is live as requested
- P1: Wire the "Apply Now" / "Reserve Your Seat" forms to a backend endpoint + email notification (currently front-end only)
- P1: Add a contact/lead capture store in MongoDB for applications
- P2: Custom domain + deploy to production
- P2: Analytics (page views, CTA clicks)
