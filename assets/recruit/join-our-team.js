var scope = document.querySelector('.aba-jt') || document;

/* ---- theme safety net. Runs only if the page CSS above did not already do the job,
   so a template change on the group site cannot leave this page boxed or double-heroed. */
try{
  if (scope.getBoundingClientRect().width && scope.getBoundingClientRect().width < window.innerWidth * 0.96){
    var el = scope.parentElement;
    while (el && el.tagName !== 'BODY' && el.tagName !== 'HTML'){
      el.style.paddingLeft = '0'; el.style.paddingRight = '0';
      el.style.maxWidth = 'none'; el.style.width = '100%';
      el = el.parentElement;
    }
  }
  var art = scope.closest('article');
  if (art){
    var th = art.querySelector(':scope > .hero-a');
    if (th && !th.contains(scope)) th.style.display = 'none';
  }
}catch(e){}
(function(){
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- reveal on scroll (pure CSS transitions, set up first so a later
       error can never leave content invisible) ---------- */
  try {
    var reveals = [].slice.call(scope.querySelectorAll('.reveal'));
    if (!reduce && 'IntersectionObserver' in window){
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(en){
          if (en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, {rootMargin:'0px 0px -8% 0px', threshold:0.05});
      reveals.forEach(function(el){ io.observe(el); });
    } else {
      reveals.forEach(function(el){ el.classList.add('in'); });
    }
    window.addEventListener('load', function(){
      reveals.forEach(function(el){
        if (!el.classList.contains('in') && el.getBoundingClientRect().top < window.innerHeight) el.classList.add('in');
      });
    });
  } catch (e) {
    scope.querySelectorAll('.reveal').forEach(function(el){ el.classList.add('in'); });
  }

  /* ---------- Apply buttons: prefill the form and jump to it ---------- */
  var sel = scope.querySelector('#f-role');
  function bindPicks(root){
    (root||document).querySelectorAll('.pick').forEach(function(b){
      if(b.dataset.bound) return;
      b.dataset.bound = '1';
      b.addEventListener('click', function(){
        var role = b.getAttribute('data-role');
        if(role){
          for(var i=0;i<sel.options.length;i++){
            if(sel.options[i].value===role || sel.options[i].text===role){ sel.selectedIndex=i; break; }
          }
        }
        scope.querySelector('#apply').scrollIntoView({behavior: reduce ? 'auto' : 'smooth'});
        setTimeout(function(){ scope.querySelector('#f-name').focus({preventScroll:true}); }, 500);
      });
    });
  }
  bindPicks(scope);

  /* ---------- roles: fan carousel (positions the cards; markup is static) ---------- */
  var fanEl = scope.querySelector('#fan');
  if(fanEl){
    var fanCards = [].slice.call(fanEl.querySelectorAll('.fan-card'));
    var fanDots  = [].slice.call(scope.querySelectorAll('#fanDots .fan-dot'));
    var active = 0, revealed = false;

    function applyTrade(card){
      var role = card.getAttribute('data-role');
      if(role){
        for(var i=0;i<sel.options.length;i++){
          if(sel.options[i].value===role || sel.options[i].text===role){ sel.selectedIndex=i; break; }
        }
      }
      scope.querySelector('#apply').scrollIntoView({behavior: reduce ? 'auto' : 'smooth'});
      setTimeout(function(){ scope.querySelector('#f-name').focus({preventScroll:true}); }, 500);
    }

    function spread(){
      var n = fanCards.length, narrow = window.innerWidth < 700;
      var step = narrow ? 84 : 150, rot = narrow ? 6 : 7, vis = narrow ? 2 : 3;
      var Y = narrow ? [0, 9, 22, 30] : [0, 12, 30, 52];
      var S = narrow ? ['1','0.9','0.8','0.74'] : ['1','0.93','0.85','0.78'];
      fanCards.forEach(function(c, i){
        var d = i - active;
        if (d > n/2) d -= n;
        if (d < -n/2) d += n;
        var ad = Math.abs(d);
        var i3 = Math.min(ad, 3);
        c.style.setProperty('--x', (d * step) + 'px');
        c.style.setProperty('--y', Y[i3] + 'px');
        c.style.setProperty('--r', (d * rot) + 'deg');
        c.style.setProperty('--s', S[i3]);
        c.style.zIndex = String(100 - ad);
        c.style.opacity = (revealed && ad <= vis) ? '1' : '0';
        c.style.pointerEvents = (revealed && ad <= vis) ? 'auto' : 'none';
        c.classList.toggle('is-active', d === 0);
        var label = c.querySelector('.go');
        if(label) label.textContent = (d === 0) ? 'Apply' : 'View roles';
      });
      fanDots.forEach(function(el, i){ el.classList.toggle('on', i === active); });
    }
    function go(i){ var n = fanCards.length; active = ((i % n) + n) % n; spread(); }
    fanCards.forEach(function(c, i){
      c.addEventListener('click', function(){ if(i === active){ applyTrade(c); } else { go(i); } });
      c.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); c.click(); } });
    });
    fanDots.forEach(function(d, i){ d.addEventListener('click', function(){ go(i); }); });
    scope.querySelector('#fanPrev').addEventListener('click', function(){ go(active - 1); });
    scope.querySelector('#fanNext').addEventListener('click', function(){ go(active + 1); });
    var rt; window.addEventListener('resize', function(){ clearTimeout(rt); rt = setTimeout(spread, 120); });
    spread();

    function revealFan(){
      revealed = true;
      spread();
      var half = fanCards.length / 2;
      fanCards.forEach(function(c, i){
        var d = Math.abs(i - active); if (d > half) d = fanCards.length - d;
        c.style.transitionDelay = (0.06 + d * 0.06).toFixed(2) + 's';
      });
      fanEl.classList.add('in');
      setTimeout(function(){ fanCards.forEach(function(c){ c.style.transitionDelay = ''; }); }, 1250);
    }
    if ('IntersectionObserver' in window){
      var fanIO = new IntersectionObserver(function(entries, obs){
        entries.forEach(function(e){ if(e.isIntersecting){ revealFan(); obs.disconnect(); } });
      }, {rootMargin:'0px 0px -10% 0px'});
      fanIO.observe(fanEl);
    } else { revealFan(); }
  }

  /* safety: never leave the cards invisible */
  setTimeout(function(){
    var f = scope.querySelector('#fan');
    if(f && !f.classList.contains('in')) f.classList.add('in');
  }, 4000);

  /* ---------- video: swap the link for an inline player (link stays as the fallback) ---------- */
  var vp = scope.querySelector('#videoPlay');
  if(vp){
    vp.addEventListener('click', function(e){
      e.preventDefault();
      scope.querySelector('#video').innerHTML =
        '<iframe src="https://www.youtube-nocookie.com/embed/BogOWR7bEA8?autoplay=1&rel=0&playsinline=1" title="aba TRADES team film" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    });
  }

  var bar = scope.querySelector('#stickybar');
  var heroEl = scope.querySelector('.hero');
  var applyEl = scope.querySelector('#apply');
  function onScroll(){
    var past = window.scrollY > heroEl.offsetHeight - 140;
    var atForm = applyEl.getBoundingClientRect().top < window.innerHeight * 0.9;
    bar.classList.toggle('on', past && !atForm);
    var h = document.documentElement.scrollHeight - window.innerHeight;
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', onScroll);
  onScroll();

  /* ---------- application form ---------- */
  var form = scope.querySelector('#applyform'), btn = scope.querySelector('#submitbtn');
  var okbox = scope.querySelector('#okbox'), errbox = scope.querySelector('#errbox');
  var endpoint = form ? (form.getAttribute('data-endpoint') || '') : '';

  /* Turnstile is only loaded when the page carries a real site key, so the
     form still works (less the bot check) before the widget is provisioned. */
  try {
    var tsBox = scope.querySelector('#turnstilebox');
    var tsKey = tsBox ? (tsBox.getAttribute('data-sitekey') || '') : '';
    if (tsKey) {
      var ts = document.createElement('script');
      ts.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
      ts.async = true; ts.defer = true;
      document.head.appendChild(ts);
    }
  } catch (e) {}

  function param(name){
    try { return new URLSearchParams(window.location.search).get(name) || ''; }
    catch (e) { return ''; }
  }
  function gaClientId(){
    try {
      var m = document.cookie.match(/(?:^|;\s*)_ga=GA\d+\.\d+\.(\d+\.\d+)/);
      return m ? m[1] : '';
    } catch (e) { return ''; }
  }

  function check(){
    var ok = form.checkValidity();
    btn.disabled = !ok;
    btn.textContent = ok ? 'Send my application' : 'Fill your name, phone, email and role to send';
  }
  form.addEventListener('input', check); form.addEventListener('change', check); check();

  form.addEventListener('submit', function(e){
    e.preventDefault();
    if (!endpoint){
      // No sink configured yet: do not pretend it was sent.
      if (errbox) errbox.style.display = 'block';
      return;
    }
    if (errbox) errbox.style.display = 'none';
    var fd = new FormData(form);
    // Source attribution, so the pipeline can report cost per applicant.
    fd.set('page_url', window.location.href.slice(0, 500));
    ['gclid','gbraid','utm_source','utm_medium','utm_campaign','utm_content','utm_term'].forEach(function(n){
      var v = param(n); if (v) fd.set(n, v.slice(0, 200));
    });
    var cid = gaClientId(); if (cid) fd.set('ga_client_id', cid);

    btn.disabled = true;
    btn.textContent = 'Sending your application...';
    fetch(endpoint, { method:'POST', body: fd })
      .then(function(r){
        return r.json().catch(function(){ return {}; }).then(function(j){
          return { ok: r.ok, status: r.status, body: j };
        });
      })
      .then(function(res){
        if (!res.ok || !res.body || !res.body.ok){
          throw new Error((res.body && res.body.error) || ('HTTP ' + res.status));
        }
        form.classList.add('sent');
        okbox.style.display = 'block';
        okbox.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block:'center'});
      })
      .catch(function(){
        if (errbox) errbox.style.display = 'block';
        btn.disabled = false;
        btn.textContent = 'Send my application';
      });
  });


  /* ---------- the 25m counter ---------- */
  var counter = scope.querySelector('[data-count]');
  if (counter && !reduce && 'IntersectionObserver' in window){
    var target = +counter.dataset.count;
    var cio = new IntersectionObserver(function(entries, obs){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        obs.disconnect();
        var t0 = null, dur = 900;
        requestAnimationFrame(function step(now){
          if(t0 === null) t0 = now;
          var p = Math.min(1, (now - t0) / dur);
          counter.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
          if(p < 1) requestAnimationFrame(step);
        });
      });
    }, {threshold:0.4});
    cio.observe(counter);
  }

})();