from fastapi import FastAPI, APIRouter, HTTPException, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
import uuid
import logging
import ipaddress
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

EMAIL_BASE_URL = "https://integrations.emergentagent.com"
EMAIL_KEY = os.environ.get("EMERGENT_EMAIL_KEY")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "The Academy")
EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO")
OWNER_EMAILS = [e.strip() for e in os.environ.get("OWNER_EMAILS", "").split(",") if e.strip()]
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

# ---------- Email guardrail gate (G2/G3 structural checks) ----------
_SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "goo.gl", "rebrand.ly")
_CRED_ASK = ("reply with your password", "reply with the code", "send your password", "cvv",
             "send us your password", "enter your password below", "confirm your card number",
             "your full card number", "seed phrase", "recovery phrase", "verify your card",
             "social security number", "confirm your bank details")
_HOSTISH = re.compile(r"\b(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)

def _host_ok(host: str) -> bool:
    if not host or "xn--" in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return not any(host == s or host.endswith("." + s) for s in _SHORTENERS)

def _same_site(shown: str, real: str) -> bool:
    return shown == real or real.endswith("." + shown) or shown.endswith("." + real)

class _EmailScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.urls, self.anchors = set(), [], []
        self._href, self._text = None, []
    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        self.urls += [v for k, v in attrs if k.lower() in ("href", "src") and v]
        if tag.lower() == "a":
            self._href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._text = []
    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, "".join(self._text)))
            self._href, self._text = None, []

def _assert_safe_email(subject: str, html: str) -> None:
    scan = _EmailScan(); scan.feed(html)
    if scan.tags & {"form", "input", "textarea", "select"}:
        raise ValueError("No forms or input fields in email (G2)")
    body = f"{subject}\n{html}".lower()
    for p in _CRED_ASK:
        if p in body:
            raise ValueError(f"Email asks the recipient for credentials: {p!r} (G2)")
    for url in scan.urls:
        low = url.strip().lower()
        if low.startswith(("mailto:", "tel:", "cid:", "#")):
            continue
        if not low.startswith("https://"):
            raise ValueError(f"Email links/assets must be absolute https: {url!r} (G3)")
        host = urlparse(low).hostname or ""
        if not _host_ok(host) or urlparse(low).username is not None:
            raise ValueError(f"Shortened, numeric-host or credential-bearing URL: {url!r} (G3)")
    for href, text in scan.anchors:
        real = urlparse(href.strip().lower()).hostname or ""
        if not real:
            continue
        for m in _HOSTISH.finditer(text):
            if not _same_site(m.group(1).lower(), real):
                raise ValueError(f"Anchor text {m.group(1)!r} != real link host {real!r} (G3)")

async def send_email(*, to: str, subject: str, html: str, reply_to: Optional[str] = None) -> Optional[str]:
    _assert_safe_email(subject, html)
    if not EMAIL_KEY:
        logger.error("EMERGENT_EMAIL_KEY not configured")
        return None
    payload = {"to": [to], "subject": subject, "html": html, "from_name": EMAIL_FROM_NAME}
    if reply_to or EMAIL_REPLY_TO:
        payload["contact_email"] = reply_to or EMAIL_REPLY_TO
    try:
        async with httpx.AsyncClient(timeout=30) as client_http:
            resp = await client_http.post(
                f"{EMAIL_BASE_URL}/api/v1/email/send",
                headers={"X-Email-Key": EMAIL_KEY},
                json=payload,
            )
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        logger.error(f"Email send error to {to}: {str(e)}")
        return None

def _row(label: str, value: str) -> str:
    return (f'<tr><td style="padding:8px 14px;font-size:13px;color:#5b6672;'
            f'font-family:Arial,sans-serif;white-space:nowrap;vertical-align:top;">{label}</td>'
            f'<td style="padding:8px 14px;font-size:14px;color:#0F1D2D;font-family:Arial,sans-serif;'
            f'font-weight:600;">{value}</td></tr>')

def _email_shell(inner: str) -> str:
    return ('<table role="presentation" width="100%" style="background:#f4f1ea;padding:24px 0;">'
            '<tr><td align="center"><table role="presentation" width="560" '
            'style="background:#ffffff;border-radius:12px;overflow:hidden;">'
            '<tr><td style="background:#0F1D2D;padding:18px 28px;font-family:Arial,sans-serif;'
            'color:#DAA017;font-weight:700;font-size:15px;letter-spacing:2px;">THE ACADEMY</td></tr>'
            f'<tr><td style="padding:28px;">{inner}</td></tr>'
            '<tr><td style="padding:16px 28px;font-family:Arial,sans-serif;font-size:11px;color:#98a2ad;'
            'border-top:1px solid #eee;">Sent by The Academy, Coimbatore. We never ask for your '
            'password or card details by email.</td></tr>'
            '</table></td></tr></table>')

# ---------- Models ----------
class ApplicationIn(BaseModel):
    name: str
    phone: str
    email: EmailStr
    interest: str
    profile: str
    city: str = ""
    form_type: str = "fullstack"
    pace: Optional[str] = None

class WorkshopBookingIn(BaseModel):
    name: str
    email: EmailStr
    phone: str
    workshop: str
    date: str
    city: str = ""

# ---------- Public endpoints ----------
@api_router.get("/health")
async def health():
    return {"status": "ok"}

@api_router.post("/applications")
async def create_application(payload: ApplicationIn):
    doc = {
        "id": str(uuid.uuid4()),
        "type": "application",
        "name": payload.name.strip(),
        "phone": payload.phone.strip(),
        "email": payload.email.strip(),
        "interest": payload.interest,
        "profile": payload.profile,
        "city": payload.city.strip(),
        "form_type": payload.form_type,
        "pace": payload.pace,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.applications.insert_one(doc)

    e = escape
    kind = "Bootcamp" if doc["form_type"] == "bootcamp" else "Full-Stack Program"
    owner_html = _email_shell(
        f'<p style="font-family:Arial,sans-serif;font-size:15px;color:#0F1D2D;margin:0 0 16px;">'
        f'<strong>New {e(kind)} application received.</strong></p>'
        '<table role="presentation">'
        + _row("Name", e(doc["name"])) + _row("Email", e(doc["email"]))
        + _row("Phone", e(doc["phone"])) + _row("City", e(doc["city"] or "—"))
        + _row("Applied for", e(doc["interest"]))
        + (_row("Preferred pace", e(doc["pace"])) if doc["pace"] else "")
        + _row("Currently", e(doc["profile"]))
        + _row("Submitted", e(doc["created_at"][:16].replace("T", " ") + " UTC"))
        + '</table>')
    applicant_html = _email_shell(
        f'<p style="font-family:Arial,sans-serif;font-size:15px;color:#0F1D2D;margin:0 0 12px;">'
        f'Hi <strong>{e(doc["name"])}</strong>, thank you for applying to The Academy.</p>'
        f'<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0 0 12px;">'
        f'We have received your application for <strong>{e(doc["interest"])}</strong>. '
        'Every application is reviewed by our admissions team, and we usually respond within '
        'one working day with next steps.</p>'
        '<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0;">'
        'Your next chapter starts here.</p>')

    emails_sent = 0
    for owner in OWNER_EMAILS:
        if await send_email(to=owner, subject=f"New {kind.lower()} application — {doc['name']}", html=owner_html):
            emails_sent += 1
    if await send_email(to=doc["email"], subject="We've received your application — The Academy",
                        html=applicant_html):
        emails_sent += 1

    return {"status": "success", "id": doc["id"], "emails_sent": emails_sent}

@api_router.post("/workshop-bookings")
async def create_workshop_booking(payload: WorkshopBookingIn):
    doc = {
        "id": str(uuid.uuid4()),
        "type": "workshop_booking",
        "name": payload.name.strip(),
        "email": payload.email.strip(),
        "phone": payload.phone.strip(),
        "workshop": payload.workshop,
        "date": payload.date,
        "city": payload.city.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.workshop_bookings.insert_one(doc)

    e = escape
    is_call = "1:1" in doc["workshop"]
    heading = "New 1:1 call request." if is_call else "New workshop seat reserved."
    owner_html = _email_shell(
        f'<p style="font-family:Arial,sans-serif;font-size:15px;color:#0F1D2D;margin:0 0 16px;">'
        f'<strong>{e(heading)}</strong></p>'
        '<table role="presentation">'
        + _row("Name", e(doc["name"])) + _row("Email", e(doc["email"]))
        + _row("Phone", e(doc["phone"])) + _row("City", e(doc["city"] or "—"))
        + _row("Type" if is_call else "Workshop", e(doc["workshop"]))
        + _row("Preferred date" if is_call else "Date", e(doc["date"]))
        + _row("Submitted", e(doc["created_at"][:16].replace("T", " ") + " UTC"))
        + '</table>')
    if is_call:
        guest_html = _email_shell(
            f'<p style="font-family:Arial,sans-serif;font-size:15px;color:#0F1D2D;margin:0 0 12px;">'
            f'Hi <strong>{e(doc["name"])}</strong>, your 1:1 call is booked.</p>'
            f'<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0 0 12px;">'
            f'Preferred date: <strong>{e(doc["date"])}</strong></p>'
            '<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0;">'
            'Our team will call you to confirm the exact time. We&#39;ll understand your goals '
            'and help you pick the right track — no pressure, no obligation.</p>')
        guest_subject = "Your 1:1 call is booked — The Academy"
        owner_subject = f"New 1:1 call request — {doc['name']} ({doc['date']})"
    else:
        guest_html = _email_shell(
            f'<p style="font-family:Arial,sans-serif;font-size:15px;color:#0F1D2D;margin:0 0 12px;">'
            f'Hi <strong>{e(doc["name"])}</strong>, your seat is reserved.</p>'
            f'<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0 0 12px;">'
            f'Workshop: <strong>{e(doc["workshop"])}</strong><br>Date: <strong>{e(doc["date"])}</strong><br>'
            'Venue: The Academy — The Institute &amp; Co-working Spaces, CovaiCare Tower, Ganapathi, Coimbatore</p>'
            '<p style="font-family:Arial,sans-serif;font-size:14px;color:#3E5166;margin:0;">'
            'We will share the exact session timing closer to the date. See you there.</p>')
        guest_subject = "Your workshop seat is reserved — The Academy"
        owner_subject = f"New workshop booking — {doc['name']} ({doc['date']})"

    emails_sent = 0
    for owner in OWNER_EMAILS:
        if await send_email(to=owner, subject=owner_subject, html=owner_html):
            emails_sent += 1
    if await send_email(to=doc["email"], subject=guest_subject, html=guest_html):
        emails_sent += 1

    return {"status": "success", "id": doc["id"], "emails_sent": emails_sent}

# ---------- CMS endpoints ----------
def require_admin(x_admin_key: Optional[str]):
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

@api_router.get("/cms/overview")
async def cms_overview(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    require_admin(x_admin_key)
    applications = await db.applications.count_documents({})
    bookings = await db.workshop_bookings.count_documents({})
    latest_app = await db.applications.find({}, {"_id": 0}).sort("created_at", -1).limit(1).to_list(1)
    latest_booking = await db.workshop_bookings.find({}, {"_id": 0}).sort("created_at", -1).limit(1).to_list(1)
    return {
        "applications": applications,
        "workshop_bookings": bookings,
        "latest_application_at": latest_app[0]["created_at"] if latest_app else None,
        "latest_booking_at": latest_booking[0]["created_at"] if latest_booking else None,
    }

@api_router.get("/cms/applications")
async def cms_applications(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    require_admin(x_admin_key)
    return await db.applications.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)

@api_router.get("/cms/workshop-bookings")
async def cms_workshop_bookings(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    require_admin(x_admin_key)
    return await db.workshop_bookings.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
