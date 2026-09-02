# PRD — The Academy Website

## Original Problem Statement
"Build a website using the html file I've uploaded." — User uploaded `the-academy-ai-upskill-site.html` (v1), then `the-academy-v3-site (6).html` (v3, current), a self-contained multi-page site for "The Academy" (Full-Stack career programs, Coimbatore).

## Follow-up Requests (2026-09-02)
1. Replace site with the new v3 HTML (old one outdated) — DONE
2. Change homepage copy "The Academy trains women" → inclusive of all audiences — DONE ("The Academy trains people from every walk of life")
3. Connect form responses to a CMS backend — DONE (MongoDB + /admin.html dashboard)
4. Workshop booking with date picker + confirmation message — DONE (modal on Apply page)
5. Apply form saves applications + instant email to owners — DONE (saving works; owner emails blocked, see below)
6. Design elevation pass: kinetic masked-line hero reveal, editorial marquee, numbered chapters, Lenis smooth scrolling, hero parallax, micro-interactions — DONE

## Architecture
- Frontend: uploaded self-contained HTML served as site root (`/app/frontend/public/index.html`); CMS dashboard at `/admin.html` (`/app/frontend/public/admin.html`); Lenis CDN for smooth scrolling; v1 React template backed up at `public/index-react-backup.html`
- Backend: FastAPI (`/app/backend/server.py`) — `POST /api/applications`, `POST /api/workshop-bookings`, `GET /api/health`, CMS: `GET /api/cms/overview|applications|workshop-bookings` (header `X-Admin-Key`)
- DB: MongoDB collections `applications`, `workshop_bookings`
- Email: Emergent managed Resend proxy (`EMERGENT_EMAIL_KEY` in backend/.env), guardrail-gated templates, from_name "The Academy", reply-to haritha@theacademyindia.com

## User Personas
- Prospective students/professionals/restarters/founders in Coimbatore exploring Full-Stack tracks (Marketing, HR, Accounting, AI & Tech)
- Academy team (Haritha, Lathika) viewing leads in the CMS

## Implemented
- 2026-08-30: v1 HTML deployed as live site root
- 2026-09-02: v3 HTML deployed; inclusive hero copy; Apply form → MongoDB + confirmation email to applicant; Workshop booking modal (topic + date picker) → MongoDB + confirmation email; CMS dashboard at /admin.html (password: walkthetalk) with stats + both lead tables; motion pass (masked line reveals on gate + home hero, slow editorial marquee, numbered chapter eyebrows, Lenis momentum scroll, hero parallax, button/pill/card hover micro-interactions); data-testids across interactive elements

## Known Issue (needs user action)
- Owner notification emails to haritha@theacademyindia.com / lathika@theacademyindia.com are rejected by the email service as UNDELIVERABLE: the domain theacademyindia.com has no MX records (no mail server configured). Fix: set up email hosting for the domain (e.g. Google Workspace / Zoho) OR give an alternative working email (e.g. Gmail) to set as OWNER_EMAILS in backend/.env. Applicant confirmation emails work fine.

## Backlog / Next Tasks
- P0: Working owner notification inbox (fix domain MX or provide alternate email)
- P1: Delete/export (CSV) actions in CMS dashboard
- P1: WhatsApp notification to owners on new application
- P2: Custom domain + production deploy
- P2: Real seat inventory per batch/workshop with live "seats left"
