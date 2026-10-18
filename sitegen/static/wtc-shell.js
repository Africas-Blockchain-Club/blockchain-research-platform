/* WeThinkCode_ shell behaviour: the SPM Interviews form's page script (spm-interviews,
   September 2026), made generic. Pair it with wtc-shell.css.

   Markup it expects (all optional except the theme button):
     <div class="stage" id="stage" aria-hidden="true"><img id="stageStill" alt="">
       <video id="stageVideo" muted loop playsinline preload="none"></video>
       <div class="shade"></div><div class="tiles" id="tiles"></div></div>
     <header class="topbar" id="topbar"> ... <button class="theme-btn" id="themeBtn"></button> ... </header>
     <figure data-photo="02_journey.jpg"><img alt=""></figure>   inside a .photo-hero

   Start it once the page is parsed:
     WTC.init({
       themeKey: 'wtc-theme',            // localStorage key; one per app is fine
       home: true,                       // this screen has the stage (photo or video background)
       still: 'data:image/jpeg;base64,...', // the home still, inlined by the server (first screen arrives ready)
       media: function (name) { ... }    // returns a Promise of a data: or blob: URL for a media slot
     });

   Rules it keeps, each learnt the hard way:
   - No scrollIntoView: it can move the page sideways. WTC.scrollToEl scrolls vertically only.
   - Apps Script pages run with <base target="_top">, so a plain #link reloads the app. Caught here.
   - Reduce motion, data saver and 2G/3G: no video, no zoom, no reveal.
   - Sections reveal once per screen; redrawing the same screen never animates again. */
(function () {
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var opts = {};
  var cache = {};
  function $(id) { return document.getElementById(id); }

  /* ------------------------------------------------------------ theme */
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  function currentTheme() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t === 'dark' || t === 'light') return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function paintThemeBtn() {
    var b = $('themeBtn'); if (!b) return;
    var dark = currentTheme() === 'dark';
    b.innerHTML = (dark ? SUN : MOON) + '<span class="t-label">' + (dark ? 'Light' : 'Dark') + '</span>';
    b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  }
  function toggleTheme() {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem(opts.themeKey || 'wtc-theme', next); } catch (e) {}
    paintThemeBtn();
  }

  /* ------------------------------------------------------------ menu */
  function wireMenu() {
    var btn = $('menuBtn'), menu = $('menu'); if (!btn || !menu) return;
    function close() { menu.classList.add('hidden'); btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = menu.classList.contains('hidden');
      menu.classList.toggle('hidden', !open); btn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) { if (!menu.contains(e.target)) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  /* ------------------------------------------------------------ media */
  function media(name) {
    if (cache[name]) return cache[name];
    if (!opts.media) return Promise.reject(new Error('No media source'));
    cache[name] = Promise.resolve(opts.media(name));
    cache[name].catch(function () { delete cache[name]; });
    return cache[name];
  }
  function videoAllowed() {
    var c = navigator.connection || {};
    return !REDUCED && !c.saveData && !/(^|-)(2g|3g)$/.test(c.effectiveType || '');
  }

  /* ------------------------------------------------------------ home stage */
  var TILES = [
    // [column, row, colour, wave] on a 4-column grid over the right of the photo.
    // Waves 1 to 3 fill in as you scroll; 'perm' tiles are there from the start.
    [2,1,'t-line','perm'],[3,1,'t-ground','w2'],[4,1,'t-ground','w1'],
    [1,2,'t-ground','w3'],[3,2,'t-line','perm'],[4,2,'t-blue','w2'],
    [2,3,'t-ground','w1'],[3,3,'t-ground','w3'],[4,3,'t-line','perm'],
    [1,4,'t-blue','w3'],[2,4,'t-line','perm'],[3,4,'t-ground','w2'],[4,4,'t-ground','w1'],
    [1,5,'t-ground','w2'],[2,5,'t-ground','w3'],[3,5,'t-blue','w1'],[4,5,'t-ground','w3']
  ];
  function showStill(url) {
    var i = $('stageStill'); if (!i || !url) return;
    i.onload = function () { i.classList.add('on'); };
    i.src = url;
  }
  function buildStage() {
    var tiles = $('tiles'); if (!tiles || tiles.childNodes.length) return;
    tiles.innerHTML = TILES.map(function (t) {
      return '<span class="tile ' + t[2] + ' ' + t[3] + '" data-row="' + t[1] + '" style="grid-column:' + t[0] + ';grid-row:' + t[1] + '"></span>';
    }).join('');
    if (opts.still) showStill(opts.still);
    else media(opts.stillSlot || '01_home_still.jpg').then(showStill, function () {});
    if (!videoAllowed() || opts.video === false) return;
    media(opts.videoSlot || '01_home_loop.mp4').then(function (u) {
      var v = $('stageVideo'); if (!v) return;
      v.addEventListener('playing', function () { v.classList.add('on'); }, { once: true });
      v.src = u;
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    }, function () {});
  }
  function onScroll() {
    var y = window.scrollY || 0, st = $('stage'), bar = $('topbar');
    var home = document.body.classList.contains('is-home');
    if (bar) bar.classList.toggle('clear', home && y < 40);
    if (!home || !st) return;
    var k = window.innerWidth < 768 ? 0.6 : 1;
    st.classList.toggle('g1', y > 40 * k); st.classList.toggle('g2', y > 180 * k); st.classList.toggle('g3', y > 380 * k);
    if (!REDUCED) st.style.setProperty('--zoom', (1 + Math.min(y, 900) / 900 * 0.08).toFixed(4));
    var v = $('stageVideo');
    if (v && v.src) {
      if (y > window.innerHeight * 1.2) { if (!v.paused) v.pause(); }
      else if (v.paused && v.classList.contains('on')) v.play().catch(function () {});
    }
  }

  /* ------------------------------------------------------------ photo headers */
  // The whole photo at its own shape beside the heading, never cropped. Missing photo:
  // the figure is removed and the band colour stands alone.
  function fillPhotos() {
    Array.prototype.forEach.call(document.querySelectorAll('figure[data-photo]'), function (fig) {
      var img = fig.querySelector('img'); if (!img) return;
      media(fig.getAttribute('data-photo')).then(function (u) {
        img.onload = function () { requestAnimationFrame(function () { img.classList.add('on'); }); };
        img.src = u;
      }, function () { if (fig.parentNode) fig.parentNode.removeChild(fig); });
    });
  }

  /* ------------------------------------------------------------ scrolling */
  function scrollToEl(el) {
    var bar = $('topbar');
    var y = el.getBoundingClientRect().top + window.scrollY - (bar ? bar.offsetHeight : 64) - 16;
    window.scrollTo({ top: Math.max(0, y), left: 0, behavior: REDUCED ? 'auto' : 'smooth' });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href').slice(1); if (!id) return;
    var el = document.getElementById(id); if (!el) return;
    e.preventDefault(); scrollToEl(el);
  });

  /* ------------------------------------------------------------ reveal once */
  var revealed = {};
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' }) : null;
  function reveal(key, selector) {
    if (revealed[key] || REDUCED || !io) { revealed[key] = true; return; }
    revealed[key] = true;
    Array.prototype.forEach.call(document.querySelectorAll(selector || '.wrap > section, .wrap .card'), function (el) {
      el.classList.add('reveal');
      var sib = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
      el.style.transitionDelay = Math.min(sib, 5) * 60 + 'ms';
      io.observe(el);
    });
  }

  /* ------------------------------------------------------------ start */
  function init(o) {
    opts = o || {};
    var b = $('themeBtn'); if (b) { b.addEventListener('click', toggleTheme); paintThemeBtn(); }
    wireMenu();
    document.body.classList.toggle('is-home', !!opts.home);
    if (opts.home) buildStage();
    fillPhotos();
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  window.WTC = { init: init, media: media, scrollToEl: scrollToEl, reveal: reveal, toggleTheme: toggleTheme, REDUCED: REDUCED };
})();
