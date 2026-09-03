
  // ---------- Nav / shell ----------
  document.addEventListener('DOMContentLoaded', function(){
    var shell = document.getElementById('siteShell');
    if(shell){ requestAnimationFrame(function(){ requestAnimationFrame(function(){ shell.classList.add('shell-visible'); }); }); }
    var path = location.pathname.replace(/\/+$/, '') || '/';
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

  // ---------- Apply page: form switcher ----------
  const switchFs = document.getElementById('switchFullstack');
  const switchBc = document.getElementById('switchBootcamp');
  if(switchFs && switchBc){
    function showForm(which){
      switchFs.classList.toggle('active', which === 'fs');
      switchBc.classList.toggle('active', which === 'bc');
      document.getElementById('applyForm').style.display = which === 'fs' ? '' : 'none';
      document.getElementById('successMsg').classList.remove('show');
      document.getElementById('bootcampForm').style.display = which === 'bc' ? '' : 'none';
      document.getElementById('bootcampSuccess').classList.remove('show');
    }
    switchFs.addEventListener('click', function(){ showForm('fs'); });
    switchBc.addEventListener('click', function(){ showForm('bc'); });
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
          city: fd.get('city'), interest: fd.get('interest'), profile: fd.get('profile'),
          pace: fd.get('pace'), form_type: 'fullstack'
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

  const bootcampFormEl = document.getElementById('bootcampForm');
  if(bootcampFormEl){
    bootcampFormEl.addEventListener('submit', async function(e){
      e.preventDefault();
      const btn = document.getElementById('bootcampSubmitBtn');
      const err = document.getElementById('bootcampError');
      err.classList.remove('show');
      btn.disabled = true; btn.textContent = 'Submitting…';
      const fd = new FormData(this);
      try{
        await postJSON('/api/applications', {
          name: fd.get('name'), phone: fd.get('phone'), email: fd.get('email'),
          city: fd.get('city'), interest: fd.get('interest'), profile: fd.get('profile'),
          form_type: 'bootcamp'
        });
        this.style.display = 'none';
        document.getElementById('bootcampSuccess').classList.add('show');
      }catch(ex){
        err.textContent = 'Something went wrong sending your application. Please try again.';
        err.classList.add('show');
        btn.disabled = false; btn.textContent = 'Apply for the Bootcamp →';
      }
    });
  }

  // ---------- 1:1 call scheduling ----------
  const callModal = document.getElementById('callModal');
  const openCallBtn = document.getElementById('openCallBtn');
  if(openCallBtn){ openCallBtn.addEventListener('click', function(){ callModal.classList.add('open'); }); }
  const closeCallBtn = document.getElementById('closeCallBtn');
  if(closeCallBtn){ closeCallBtn.addEventListener('click', function(){ callModal.classList.remove('open'); }); }
  if(callModal){ callModal.addEventListener('click', function(e){ if(e.target === callModal) callModal.classList.remove('open'); }); }
  const callDateEl = document.getElementById('callDate');
  if(callDateEl){ callDateEl.min = new Date().toISOString().split('T')[0]; }
  const callFormEl = document.getElementById('callForm');
  if(callFormEl){
    callFormEl.addEventListener('submit', async function(e){
      e.preventDefault();
      const btn = document.getElementById('callSubmitBtn');
      const err = document.getElementById('callError');
      err.classList.remove('show');
      btn.disabled = true; btn.textContent = 'Booking…';
      const fd = new FormData(this);
      const payload = { name: fd.get('name'), email: fd.get('email'), phone: fd.get('phone'),
        city: fd.get('city'), workshop: '1:1 Track-Match Call', date: fd.get('date') };
      try{
        await postJSON('/api/workshop-bookings', payload);
        this.style.display = 'none';
        document.getElementById('callSuccessText').textContent =
          'Preferred date: ' + payload.date + ' — we will call you to confirm the exact time and help you pick the right track.';
        document.getElementById('callSuccess').classList.add('show');
      }catch(ex){
        err.textContent = 'Could not book your call just now. Please try again.';
        err.classList.add('show');
        btn.disabled = false; btn.textContent = 'Request My Call →';
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
