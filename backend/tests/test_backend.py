import os
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "https://web-launch-demo-2.preview.emergentagent.com").rstrip("/")
ADMIN_KEY = "walkthetalk"


def test_health():
    r = requests.get(f"{BASE}/api/health", timeout=15)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_fullstack_application():
    payload = {
        "name": "QA Fullstack",
        "phone": "9876543210",
        "email": "qa.fullstack@example.com",
        "interest": "The Full-Stack Marketer",
        "profile": "Working Professional",
        "city": "Coimbatore",
        "form_type": "fullstack",
        "pace": "Weekend Pace — 3 Months",
    }
    r = requests.post(f"{BASE}/api/applications", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "success"
    app_id = body["id"]

    # Verify via CMS
    r2 = requests.get(f"{BASE}/api/cms/applications", headers={"X-Admin-Key": ADMIN_KEY}, timeout=15)
    assert r2.status_code == 200
    recs = r2.json()
    match = next((x for x in recs if x["id"] == app_id), None)
    assert match is not None
    assert match["city"] == "Coimbatore"
    assert match["form_type"] == "fullstack"
    assert match["pace"] == "Weekend Pace — 3 Months"


def test_bootcamp_application():
    payload = {
        "name": "QA Bootcamp",
        "phone": "9876543211",
        "email": "qa.bootcamp@example.com",
        "interest": "Practical Cost Analyst — Sep 14–19 (7-Day Bootcamp · 25 Hours)",
        "profile": "College Student",
        "city": "Chennai",
        "form_type": "bootcamp",
    }
    r = requests.post(f"{BASE}/api/applications", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    app_id = r.json()["id"]
    r2 = requests.get(f"{BASE}/api/cms/applications", headers={"X-Admin-Key": ADMIN_KEY}, timeout=15)
    match = next((x for x in r2.json() if x["id"] == app_id), None)
    assert match is not None
    assert match["form_type"] == "bootcamp"
    assert match["city"] == "Chennai"


def test_call_booking():
    payload = {
        "name": "QA Call",
        "email": "qa.call@example.com",
        "phone": "9876543212",
        "workshop": "1:1 Track-Match Call",
        "date": "2026-02-15",
        "city": "Bangalore",
    }
    r = requests.post(f"{BASE}/api/workshop-bookings", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    bid = r.json()["id"]
    r2 = requests.get(f"{BASE}/api/cms/workshop-bookings", headers={"X-Admin-Key": ADMIN_KEY}, timeout=15)
    match = next((x for x in r2.json() if x["id"] == bid), None)
    assert match is not None
    assert match["city"] == "Bangalore"
    assert match["workshop"] == "1:1 Track-Match Call"


def test_admin_auth_rejects_bad_key():
    r = requests.get(f"{BASE}/api/cms/applications", headers={"X-Admin-Key": "wrong"}, timeout=15)
    assert r.status_code == 401
