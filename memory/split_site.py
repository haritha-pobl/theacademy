import re, os, base64

SRC = '/app/frontend/public/index.html'
PUB = '/app/frontend/public'
html = open(SRC, encoding='utf-8').read()

# ---------- 1. extract base64 images ----------
os.makedirs(f'{PUB}/assets', exist_ok=True)
imgs = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', html)
names = {}
seen = {}
idx = 0
labels = ['logo-gate', 'logo-topbar', 'logo-footer']
for i, b64 in enumerate(imgs):
    if b64 in seen:
        names[i] = seen[b64]
        continue
    fname = f'assets/{labels[i]}.png'
    with open(f'{PUB}/{fname}', 'wb') as f:
        f.write(base64.b64decode(b64))
    seen[b64] = fname
    names[i] = fname

counter = [0]
def repl(m):
    fname = names[counter[0]]
    counter[0] += 1
    return f'/{fname}'
html = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', repl, html)

# ---------- 2. extract CSS ----------
css = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
open(f'{PUB}/assets/site.css', 'w', encoding='utf-8').write(css)

# ---------- 3. head template ----------
def head(title):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body class="entered">
'''

# ---------- 4. grab sections ----------
def between(start, end):
    i = html.index(start)
    j = html.index(end, i)
    return html[i:j]

gate = between('<div id="landingGate">', '<div id="siteShell">')
topbar = between('<div class="topbar">', '<!-- ================= HERO')
home_main = between('<main id="home"', '<main id="story"').replace('<!-- ================= STORY ================= -->', '')
story_main = between('<main id="story"', '<main id="programs"').replace('<!-- ================= PROGRAMS ================= -->', '')
programs_main = between('<main id="programs"', '<main id="outcomes"').replace('<!-- ================= OUTCOMES ================= -->', '')
outcomes_main = between('<main id="outcomes"', '<main id="apply"').replace('<!-- ================= FINAL CTA ================= -->', '')
apply_main = between('<main id="apply"', '<div class="wk-modal"')
wk_modal = between('<div class="wk-modal"', '<footer>')
footer = between('<footer>', '</div><!-- /siteShell -->') 

# ---------- 5. rewrite nav to real links ----------
topbar = topbar.replace(
    '<button class="tab-btn active" data-page="home" data-testid="nav-tab-home">Home</button>',
    '<a class="tab-btn" href="/home/" data-nav="home" data-testid="nav-tab-home">Home</a>')
topbar = topbar.replace(
    '<button class="tab-btn" data-page="story" data-testid="nav-tab-story">Why The Academy</button>',
    '<a class="tab-btn" href="/why/" data-nav="why" data-testid="nav-tab-story">Why The Academy</a>')
topbar = topbar.replace(
    '<button class="tab-btn" data-page="programs" data-testid="nav-tab-programs">Programs</button>',
    '<a class="tab-btn" href="/programs/" data-nav="programs" data-testid="nav-tab-programs">Programs</a>')
topbar = topbar.replace(
    '<a href="#" class="apply-btn" data-page="apply" data-testid="nav-apply-button">Apply Now</a>',
    '<a href="/apply/" class="apply-btn" data-nav="apply" data-testid="nav-apply-button">Apply Now</a>')
topbar = topbar.replace(
    '<div id="navLogo" style="cursor:pointer;display:flex;align-items:center;" title="Back to landing page">',
    '<a id="navLogo" href="/" style="cursor:pointer;display:flex;align-items:center;" title="Back to landing page">')
# close the anchor that replaced navLogo div: the img line ends then </div> follows
topbar = topbar.replace('</div>\n    <div class="tabs" id="tabs">', '</a>\n    <div class="tabs" id="tabs">', 1)

# footer links
footer = footer.replace('<a href="#persona">Find Your Chapter</a>', '<a href="/home/#persona">Find Your Chapter</a>')
footer = footer.replace('<a href="#apply" data-page="apply">Apply</a>', '<a href="/apply/">Apply</a>')

# in-page links inside mains
programs_main = programs_main.replace('<a href="#apply" class="btn-gold" data-page="apply">Apply to a Signature Program →</a>',
                                      '<a href="/apply/" class="btn-gold">Apply to a Signature Program →</a>')

# keep mains visible
for name in ['home', 'story', 'programs', 'outcomes', 'apply']:
    pass  # mains keep class="page"; site.css .page{display:none} -> we add active below

home_main = home_main.replace('<main id="home" class="page active">', '<main id="home" class="page active">')
story_main = story_main.replace('<main id="story" class="page">', '<main id="story" class="page active">')
programs_main = programs_main.replace('<main id="programs" class="page">', '<main id="programs" class="page active">')
outcomes_main = outcomes_main.replace('<main id="outcomes" class="page">', '<main id="outcomes" class="page active">')
apply_main = apply_main.replace('<main id="apply" class="page">', '<main id="apply" class="page active">')

# ---------- 6. shared JS ----------
site_js = '''
  // ---------- Nav / shell ----------
  document.addEventListener('DOMContentLoaded', function(){
    var shell = document.getElementById('siteShell');
    if(shell){ requestAnimationFrame(function(){ requestAnimationFrame(function(){ shell.classList.add('shell-visible'); }); }); }
    var path = location.pathname.replace(/\\/+$/, '') || '/';
    var key = path === '/' ? 'home' : path.split('/').filter(Boolean)[0];
    document.querySelectorAll('.tab-btn[data-nav], .apply-btn[data-nav]').forEach(function(el){
      if(el.getAttribute('data-nav') === key) el.classList.add('active');
    });
  });
  var mobileToggleEl = document.getElementById('mobileToggle');
  if(mobileToggleEl){
    mobileToggleEl.addEventListener('click', function(){
      document.getElementById('tabs').classList.toggle('open');
    });
  }

  // ---------- Native scrolling + hero parallax ----------
  window.addEventListener('scroll', function(){
    var home = document.getElementById('home');
    if(home){
      var y = window.scrollY;
      var hero = document.querySelector('.hero');
      var heroInner = document.querySelector('.hero-inner');
      if(hero) hero.style.setProperty('--py', (y * 0.22) + 'px');
      if(heroInner) heroInner.style.transform = 'translateY(' + (y * 0.07) + 'px)';
    }
  }, { passive: true });

  // ---------- Forms -> CMS backend ----------
  async function postJSON(url, payload){
    const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    if(!res.ok) throw new Error('Request failed');
    return res.json();
  }

  const applyFormEl = document.getElementById('applyForm');
  if(applyFormEl){
    applyFormEl.addEventListener('submit', async function(e){
      e.preventDefault();
      const btn = document.getElementById('applySubmitBtn');
      const err = document.getElementById('applyError');
      err.classList.remove('show');
      btn.disabled = true; btn.textContent = 'Submitting…';
      const fd = new FormData(this);
      try{
        await postJSON('/api/applications', {
          name: fd.get('name'), phone: fd.get('phone'), email: fd.get('email'),
          interest: fd.get('interest'), profile: fd.get('profile')
        });
        this.style.display = 'none';
        document.getElementById('successMsg').classList.add('show');
      }catch(ex){
        err.textContent = 'Something went wrong sending your application. Please try again.';
        err.classList.add('show');
        btn.disabled = false; btn.textContent = 'Submit Application →';
      }
    });
  }

  // ---------- Workshop booking ----------
  const wkModal = document.getElementById('workshopModal');
  const openWkBtn = document.getElementById('openWorkshopBtn');
  if(openWkBtn){ openWkBtn.addEventListener('click', function(){ wkModal.classList.add('open'); }); }
  const closeWkBtn = document.getElementById('closeWorkshopBtn');
  if(closeWkBtn){ closeWkBtn.addEventListener('click', function(){ wkModal.classList.remove('open'); }); }
  if(wkModal){ wkModal.addEventListener('click', function(e){ if(e.target === wkModal) wkModal.classList.remove('open'); }); }
  const wkDateEl = document.getElementById('workshopDate');
  if(wkDateEl){ wkDateEl.min = new Date().toISOString().split('T')[0]; }
  const wkFormEl = document.getElementById('workshopForm');
  if(wkFormEl){
    wkFormEl.addEventListener('submit', async function(e){
      e.preventDefault();
      const btn = document.getElementById('workshopSubmitBtn');
      const err = document.getElementById('workshopError');
      err.classList.remove('show');
      btn.disabled = true; btn.textContent = 'Reserving…';
      const fd = new FormData(this);
      const payload = { name: fd.get('name'), email: fd.get('email'), phone: fd.get('phone'), workshop: fd.get('workshop'), date: fd.get('date') };
      try{
        await postJSON('/api/workshop-bookings', payload);
        this.style.display = 'none';
        document.getElementById('workshopSuccessText').textContent =
          payload.workshop + ' · ' + payload.date + ' — a confirmation email is on its way to you. Venue: The Academy, CovaiCare Tower, Ganapathi, Coimbatore.';
        document.getElementById('workshopSuccess').classList.add('show');
      }catch(ex){
        err.textContent = 'Could not reserve your seat just now. Please try again.';
        err.classList.add('show');
        btn.disabled = false; btn.textContent = 'Confirm My Seat →';
      }
    });
  }

  // ---------- Persona selector ----------
  const personaContent = {
    student: {
      eyebrow: "For students, exploring",
      title: "Get campus-to-corporate ready — before you graduate.",
      body: "Explore real business functions, build a portfolio, and walk out placement-ready faster than your batchmates — with AI fluency most institutes still aren't teaching."
    },
    professional: {
      eyebrow: "For professionals, feeling outdated",
      title: "AI changed the game. Make sure you're playing it.",
      body: "A 3-hour workshop or a 12-week signature track — refresh the skills that went stale, without pausing your career to do it."
    },
    restarter: {
      eyebrow: "For anyone restarting,",
      title: "The industry moved. So can you — faster than you think.",
      body: "Real, applied training and a campus built around your actual life — including on-site support — so the logistics stop being the reason you don't begin."
    },
    founder: {
      eyebrow: "For founders, building",
      title: "Learn what you'd need an MBA for — while you build.",
      body: "Business fundamentals across marketing, HR, and finance, plus a direct line into POBL's founder and mentor network as you go."
    }
  };
  const cards = document.querySelectorAll('.persona-card');
  const msgBox = document.getElementById('personaMessage');
  cards.forEach(card => {
    card.addEventListener('click', function(){
      cards.forEach(c => c.classList.remove('selected'));
      this.classList.add('selected');
      const data = personaContent[this.getAttribute('data-persona')];
      msgBox.style.opacity = 0;
      setTimeout(()=>{
        msgBox.querySelector('.p-eyebrow').textContent = data.eyebrow;
        msgBox.querySelector('h3').textContent = data.title;
        msgBox.querySelector('p').textContent = data.body;
        msgBox.style.opacity = 1;
      }, 200);
    });
  });

  // ---------- Curriculum toggles ----------
  function toggleModules(id){
    document.getElementById(id).classList.toggle('open');
  }
  function toggleLevel2(id, btn){
    document.getElementById('l2-' + id).classList.toggle('open');
    btn.classList.toggle('open');
  }
  function toggleSpec(id, btn){
    const trigger = btn || event.currentTarget;
    const scope = trigger.closest('.modules');
    scope.querySelectorAll('.mkt-spec-btn').forEach(b=>b.classList.remove('active'));
    scope.querySelectorAll('.mkt-spec-panel').forEach(p=>p.classList.remove('active'));
    trigger.classList.add('active');
    scope.querySelector('#spec-'+id).classList.add('active');
  }

  // ---------- Scroll reveal ----------
  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('in-view');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
  document.querySelectorAll('.reveal').forEach((el,i) => {
    el.style.transitionDelay = (i % 4) * 0.06 + 's';
    revealObserver.observe(el);
  });
'''
open(f'{PUB}/assets/site.js', 'w', encoding='utf-8').write(site_js)

# ---------- 7. build pages ----------
def page(title, mains, with_modal=False):
    parts = [head(title), '<div id="siteShell">\n', topbar]
    parts += mains
    if with_modal:
        parts.append(wk_modal)
    parts.append(footer)
    parts.append('</div><!-- /siteShell -->\n\n<script src="/assets/site.js"></script>\n</body>\n</html>\n')
    return ''.join(parts)

os.makedirs(f'{PUB}/home', exist_ok=True)
os.makedirs(f'{PUB}/why', exist_ok=True)
os.makedirs(f'{PUB}/programs', exist_ok=True)
os.makedirs(f'{PUB}/outcomes', exist_ok=True)
os.makedirs(f'{PUB}/apply', exist_ok=True)

open(f'{PUB}/home/index.html', 'w', encoding='utf-8').write(page('The Academy — Your Next Chapter', [home_main]))
open(f'{PUB}/why/index.html', 'w', encoding='utf-8').write(page('Why The Academy', [story_main]))
open(f'{PUB}/programs/index.html', 'w', encoding='utf-8').write(page('Programs — The Academy', [programs_main]))
open(f'{PUB}/outcomes/index.html', 'w', encoding='utf-8').write(page('Outcomes — The Academy', [outcomes_main]))
open(f'{PUB}/apply/index.html', 'w', encoding='utf-8').write(page('Apply — The Academy', [apply_main], with_modal=True))

# ---------- 8. landing page (/) ----------
gate = gate.replace(
    '<button class="btn-gold" id="enterSiteBtn" data-testid="enter-site-button">Enter The Academy &rarr;</button>',
    '<a class="btn-gold" id="enterSiteBtn" href="/home/" data-testid="enter-site-button">Enter The Academy &rarr;</a>')

landing = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Academy — Your Next Chapter</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>

{gate}
</body>
</html>
'''
open(f'{PUB}/index.html', 'w', encoding='utf-8').write(landing)
print('DONE')
for p in ['index.html','home/index.html','why/index.html','programs/index.html','outcomes/index.html','apply/index.html','assets/site.css','assets/site.js']:
    print(p, os.path.getsize(f'{PUB}/{p}'))
