# The Academy — Website + CMS PRD

## Original Problem Statement
Update the site using provided HTML (`the-academy-v3-site (6).html`). Make homepage copy inclusive (not "trains women" only). Connect forms to a CMS backend. Add Workshop Booking (date picker + confirmation) and Apply Form that saves applications and sends instant email notifications. Awwwards-level motion/UI.

## Architecture
- Frontend: static HTML/CSS/JS served from `/app/frontend/public/index.html` (bypasses React), admin CMS at `/admin.html`
- Backend: FastAPI (`/app/backend/server.py`) + MongoDB
- Email: Emergent Email Integration (Resend-backed) via `EMERGENT_EMAIL_KEY`

## Key Endpoints
- `POST /api/applications`
- `POST /api/workshop-bookings`
- `GET /api/cms/overview|applications|workshop-bookings` (header `X-Admin-Key`)

## DB Collections
- applications: {id, name, phone, email, interest, profile, created_at}
- workshop_bookings: {id, name, email, phone, workshop, date, created_at}

## Credentials / Config
- Admin CMS password: `walkthetalk` (env `ADMIN_KEY`)
- `OWNER_EMAILS` (backend/.env): thari0907@gmail.com, haritha@theacademyindia.com, lathika@theacademyindia.com

## Implemented (as of June 2026)
- V3 site live with inclusive copy + high-motion design (DONE)
- Apply + Workshop booking forms → DB + emails (DONE, tested)
- CMS dashboard at /admin.html (DONE)
- Owner notification fallback: added thari0907@gmail.com — verified 202 Accepted (2026-06)
- Scroll fix: removed Lenis scroll-hijacking, restored native scrolling with passive-listener hero parallax (tested, 2026-06)
- CSV export: one-click "Download CSV" per tab in CMS dashboard, Excel-friendly BOM (tested, 2026-06)

## Known Issue (user-side, not code)
- `theacademyindia.com` has NO MX records (verified via Google DNS + port-25 probe). Mail to haritha@/lathika@ that domain bounces (422 from provider). User reads mail via Google Workspace → needs to add Google MX record at DNS host (nameservers dns1-4.p07.nsone.net, likely Squarespace):
  - MX: `@` → `smtp.google.com`, priority 1
  - Once added (up to a few hours to propagate), re-test — code needs no change since addresses are already in OWNER_EMAILS.

## Backlog
- P2: WhatsApp alerts on new application/booking — user chose to SKIP for now (no provider account). Alert number saved for later: +91 9940862795 (Twilio account needed)
