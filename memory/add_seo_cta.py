import re

PUB = '/app/frontend/public'
BASE = 'https://web-launch-demo-2.preview.emergentagent.com'

PAGES = {
    'index.html': {
        'path': '/',
        'title': 'The Academy, Coimbatore — Your Next Chapter | AI-Integrated Business Programs',
        'desc': "The Academy trains you in a real, certified Full-Stack specialization — Marketing, HR, Accounting, or AI & Technology. Practitioner-led, AI-integrated, and built to move you toward a placement. Founding Cohort now open in Coimbatore.",
        'cta': True,
    },
    'home/index.html': {
        'path': '/home/',
        'title': 'The Academy — AI-Integrated Business Skills Training in Coimbatore',
        'desc': "Practitioner-led business education for students, professionals, restarters and founders. Full-Stack programs in Marketing, People Operations (HR), Accounting and AI & Technology — backed by POBL.",
        'cta': True,
    },
    'why/index.html': {
        'path': '/why/',
        'title': 'Why The Academy — Practitioner-Led, Applied, Built for Real Life',
        'desc': "We named ourselves after what happens next. Built and backed by POBL's founder ecosystem: applied training, real capstones, and a campus designed around how your life actually runs.",
        'cta': True,
    },
    'programs/index.html': {
        'path': '/programs/',
        'title': 'Programs — Full-Stack Marketing, HR, Accounting & AI | The Academy',
        'desc': "Four signature Full-Stack tracks: Marketer, HR Professional, Accountant, and AI & Technology Professional. 30-hour Foundation plus one deep AI-powered specialization, ending in a live capstone and placement pipeline.",
        'cta': True,
    },
    'outcomes/index.html': {
        'path': '/outcomes/',
        'title': 'Outcomes — Proof, Not Promises | The Academy',
        'desc': "Four signature Full-Stack tracks, 12-week programs, a live capstone every cohort, and a 100% AI-integrated curriculum. Verified placement data added as each cohort completes its Proof of Work Showcase.",
        'cta': True,
    },
    'apply/index.html': {
        'path': '/apply/',
        'title': 'Apply Now — Founding Cohort | The Academy, Coimbatore',
        'desc': "Applications for The Academy's Founding Cohort are open. Apply in under 3 minutes, reserve a 3-hour workshop seat, and get matched to the right Full-Stack track. Limited seats, rolling review.",
        'cta': False,
    },
}

def seo_block(p):
    url = BASE + p['path']
    return f'''<meta name="description" content="{p['desc']}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0F1D2D">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Academy">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/og-card.jpg">
<meta property="og:image:width" content="1264">
<meta property="og:image:height" content="848">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{p['title']}">
<meta name="twitter:description" content="{p['desc']}">
<meta name="twitter:image" content="{BASE}/assets/og-card.jpg">'''

CTA = '<a class="float-cta" href="/apply/" data-testid="floating-apply-cta">Apply Now — Founding Cohort</a>\n'

for fname, p in PAGES.items():
    fp = f'{PUB}/{fname}'
    html = open(fp, encoding='utf-8').read()
    # title
    html = re.sub(r'<title>.*?</title>', f'<title>{p["title"]}</title>', html, count=1)
    # drop any prior seo block (idempotent)
    html = re.sub(r'<meta name="description".*?<meta name="twitter:image"[^>]*>\n?', '', html, flags=re.S)
    html = html.replace('</title>', '</title>\n' + seo_block(p), 1)
    # floating CTA
    html = html.replace(CTA, '')
    if p['cta']:
        m = re.search(r'<body[^>]*>\n?', html)
        html = html[:m.end()] + '\n' + CTA + html[m.end():]
    open(fp, 'w', encoding='utf-8').write(html)
    print('done', fname)

# admin: noindex
fp = f'{PUB}/admin.html'
html = open(fp, encoding='utf-8').read()
if 'noindex' not in html:
    html = html.replace('<title>', '<meta name="robots" content="noindex, nofollow">\n<title>', 1)
    open(fp, 'w', encoding='utf-8').write(html)
    print('done admin.html (noindex)')
