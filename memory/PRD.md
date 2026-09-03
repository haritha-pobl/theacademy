# The Academy — Website + CMS PRD

## Original Problem Statement
Update the site using provided HTML (`the-academy-v3-site (6).html`). Make homepage copy inclusive (not "trains women" only). Connect forms to a CMS backend. Add Workshop Booking (date picker + confirmation) and Apply Form that saves applications and sends instant email notifications. Awwwards-level motion/UI.

## Architecture
- Frontend: static multi-page HTML site served from `/app/frontend/public/`:
  - `/` = landing gate page (Enter → /home/)
  - `/home/`, `/why/`, `/programs/`, `/apply/` = individual pages with real URLs (trailing slash required)
  - `/outcomes/` exists but is intentionally NOT in nav
  - `/admin.html` = CMS dashboard
  - Shared assets: `/assets/site.css`, `/assets/site.js`, `/assets/logo-*.png`
  - Backup of old single-page version: `/app/memory/index-singlepage-backup.html`; splitter script: `/app/memory/split_site.py`
- Backend: FastAPI (`/app/backend/server.py`) + MongoDB
- Email: Emergent Email Integration (Resend-backed) via `EMERGENT_EMAIL_KEY`

## Key Endpoints
- `POST /api/applications`
- `POST /api/workshop-bookings`
- `GET /api/cms/overview|applications|workshop-bookings` (header `X-Admin-Key`)

## DB Collections
- applications: {id, name, phone, email, city, interest, profile, pace, form_type(fullstack|bootcamp), created_at}
- workshop_bookings: {id, name, email, phone, city, workshop, date, created_at} — also stores 1:1 call requests (workshop="1:1 Track-Match Call")

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
- Nav cleanup: removed Outcomes & Landing tabs from top nav; Signature badge right-aligned on all course cards; Level 2 sections now collapsed by default with animated expand toggle (mkt/hr/tech); Full-Stack Accountant restructured — all 5 modules under Foundation, no Level 2 (screenshot-verified, 2026-06)
- Multi-page restructure: converted CSS/JS tab navigation to individual pages with real URLs (/, /home/, /why/, /programs/, /apply/); nav = real links with active state; base64 logos extracted to /assets/*.png; shared site.css/site.js. Full regression by testing agent — 100% pass (2026-06)
- Floating left-edge "Apply Now — Founding Cohort" CTA on all pages except /apply/, links straight to the form page (screenshot-verified, 2026-06)
- SEO: unique titles + meta descriptions + canonical + Open Graph/Twitter cards per page, generated branded og-card.jpg, admin.html noindex. NOTE: og:url/og:image use the preview domain as base (script: /app/memory/add_seo_cta.py, BASE var) — update BASE and rerun after deploying to the final domain (2026-06)
- Mobile/tablet fix: landing gate changed from position:fixed/overflow:hidden (unscrollable on phones) to position:relative + min-height:100dvh with responsive gate sizing (logo 112/92/68px) and body overflow-x:hidden. Verified by testing agent at 360/390/820/1920 widths — 100% pass (2026-06)
- Admissions restructure (2026-06, testing agent pass): floating CTA text → "Apply Now"; all "Founding Cohort" wording → "Admissions Now Open"/"first batch"; programs page bootcamp cards updated (Cost Analyst 25 hrs, next batch Sep 14–19 7-day; Digital Marketing 7-day same week; no Format lines); "3-Hour Skill Workshops — Coming Soon" card; pace explainer cards (Weekend 3-month vs Full-Time 1-month with audience tags); apply page now has TWO forms (Full-Stack with pace radio + Bootcamp) both with City field, plus "Schedule a Free 1:1 Call" modal (posts to workshop-bookings as "1:1 Track-Match Call"); backend ApplicationIn: +city/form_type/pace, BookingIn: +city, conditional 1:1-call email copy; CMS shows City/Type/Pace columns + updated CSV, tab renamed "Calls & Bookings"

## Known Issue (user-side, not code)
- `theacademyindia.com` has NO MX records (verified via Google DNS + port-25 probe). Mail to haritha@/lathika@ that domain bounces (422 from provider). User reads mail via Google Workspace → needs to add Google MX record at DNS host (nameservers dns1-4.p07.nsone.net, likely Squarespace):
  - MX: `@` → `smtp.google.com`, priority 1
  - Once added (up to a few hours to propagate), re-test — code needs no change since addresses are already in OWNER_EMAILS.

## Backlog
- P2: WhatsApp alerts on new application/booking — user chose to SKIP for now (no provider account). Alert number saved for later: +91 9940862795 (Twilio account needed)
