/* ============================================================
   INTRO SPLASH — the overlay markup lives directly in index.html
   (#kp-intro) so it is visible from the first paint. This script
   only manages playback and dismissal. Shows on every page load.
   ============================================================ */
(function () {
  function initIntro() {
    var intro = document.getElementById('kp-intro');
    if (!intro) return;

    // ?nointro — skip the splash entirely (testing / direct links)
    if (/[?&]nointro/.test(location.search)) {
      if (intro.parentNode) intro.parentNode.removeChild(intro);
      return;
    }

    var v = document.getElementById('kp-intro-video');
    var tapBtn = document.getElementById('kp-intro-tap');
    var dismissed = false;
    var playing = false;
    var endTimer = null;

    document.documentElement.classList.add('kp-intro-active');
    document.body.classList.add('kp-intro-active');

    v.muted = true;
    v.defaultMuted = true;
    v.playsInline = true;

    function dismiss() {
      if (dismissed) return;
      dismissed = true;
      // tell the hero to snap its background video to the final frame
      // BEFORE the overlay fades, so the handoff is seamless
      try { document.dispatchEvent(new CustomEvent('kp:intro-done')); } catch (e) { }
      intro.style.transition = 'opacity .45s ease';
      intro.style.opacity = '0';
      intro.style.pointerEvents = 'none';
      document.documentElement.classList.remove('kp-intro-active');
      document.body.classList.remove('kp-intro-active');
      setTimeout(function () {
        if (intro.parentNode) intro.parentNode.removeChild(intro);
      }, 500);
    }

    function showTapPrompt() { intro.classList.add('needs-tap'); }
    function hideTapPrompt() { intro.classList.remove('needs-tap'); }

    // the clip's closing shot is a held world-map frame — play the video in
    // full, but once that shot arrives keep it for only ~0.3s, then cut away
    var mapHoldTimer = null;
    v.addEventListener('timeupdate', function () {
      if (mapHoldTimer || !isFinite(v.duration) || v.duration <= 0) return;
      if (v.currentTime >= v.duration - 5.5) {
        mapHoldTimer = setTimeout(dismiss, 300);
      }
    });

    v.addEventListener('ended', function () {
      try { v.pause(); } catch (e) { }
      setTimeout(dismiss, 400);
    });

    v.addEventListener('playing', function () {
      playing = true;
      hideTapPrompt();
      if (endTimer) return;
      var dur = isFinite(v.duration) && v.duration > 0 ? v.duration : 15;
      endTimer = setTimeout(dismiss, (dur + 2.5) * 1000);
    });

    v.addEventListener('error', function () {
      if (!playing) showTapPrompt();
    });

    setTimeout(dismiss, 45000);

    tapBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      hideTapPrompt();
      v.muted = true;
      v.play().catch(showTapPrompt);
    });

    function tryPlay() {
      var p;
      try { p = v.play(); } catch (e) { showTapPrompt(); return; }
      if (p && typeof p.then === 'function') {
        p.then(hideTapPrompt).catch(showTapPrompt);
      }
    }
    tryPlay();
    v.addEventListener('loadeddata', function () { if (!playing) tryPlay(); });
    v.addEventListener('canplay', function () { if (!playing) tryPlay(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initIntro);
  } else {
    initIntro();
  }
})();

/* The broken Revolution Slider is handled per page:
   - Homepage: replaced by an immersive scroll hero — home_video.mp4 fills the
     viewport as the landing background and scrubs with the visitor's scroll
     (driven by the shared .kp-scrolly engine below); headline + CTAs float on top.
   - Subpages (e.g. Für Arbeitgeber): the slider hero only repeated the landing,
     so it is removed entirely — the page opens directly on its content. */
(function () {
  function buildHero() {
    var wrap = document.querySelector('rs-module-wrap, .rev_slider_wrapper');
    if (!wrap || wrap.dataset.bgLocalDone) return;
    wrap.dataset.bgLocalDone = '1';

    var section = wrap.closest('section') || wrap.parentNode;

    // strip runaway slider height forcers (e.g. 99985px spacers) on every page
    document.querySelectorAll('rs-fw-forcer').forEach(function (f) {
      if (f.parentNode) f.parentNode.removeChild(f);
    });

    if (!document.body.classList.contains('home')) {
      if (section && section.parentNode) section.parentNode.removeChild(section);
      // the fixed header no longer overlaps a hero - pad the content instead
      document.body.classList.add('kp-no-hero');
      return;
    }

    // Static, on-theme hero — the scroll-scrub world video was removed; the
    // brand lockup, claim and CTAs sit on the house green/gold gradient.
    var hero = document.createElement('section');
    hero.className = 'kp-hero-static';
    hero.id = 'kp-hero';
    hero.innerHTML =
      '<div class="kp-hero-static__overlay" aria-hidden="true"></div>' +
      '<div class="kp-hero-static__content">' +
      '<img class="kp-hero-brand__mark" src="assets/logo-mark.png" alt="Kastell Personalberatung">' +
      '<h1 class="kp-hero-brand__name">Kastell <span>Personalberatung</span></h1>' +
      '<span class="kp-hero-brand__rule" aria-hidden="true"></span>' +
      '<h2 class="kp-hero-brand__claim">Ihr Partner f&uuml;r Personalsuche &amp; HR Advisory.</h2>' +
      '<p class="kp-hero-static__sub">Wir finden das Top-Match f&uuml;r Ihr Team &ndash; in IT, Engineering und Financial Services.</p>' +
      '<div class="kp-hero-static__btns">' +
      '<a class="kp-hero-static__btn" href="candidates.html">Ich bin Kandidat:in</a>' +
      '<a class="kp-hero-static__btn" href="employers.html">Ich bin Arbeitgeber</a>' +
      '</div>' +
      '</div>';
    section.parentNode.replaceChild(hero, section);

    var revealed = false;
    var reveal = function () {
      if (revealed) return;
      revealed = true;
      hero.classList.add('is-revealed');
    };

    if (document.getElementById('kp-intro')) {
      // content fades in the moment the intro splash hands off
      document.addEventListener('kp:intro-done', reveal, { once: true });
      setTimeout(reveal, 4000); // never leave the hero text hidden
    } else {
      reveal();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildHero);
  } else {
    buildHero();
  }
  // safety: run again after full load in case revslider rebuilt its wrapper
  window.addEventListener('load', buildHero);
})();

/* ============================================================
   About Us — sticky team cards: IntersectionObserver reveal.
   Adds `is-visible` class when a card enters the viewport so the
   CSS transitions (fade + slide) fire.
   ============================================================ */
(function () {
  function boot() {
    var cards = document.querySelectorAll('[data-sticky-card]');
    if (!cards.length) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        } else {
          // Remove class when card scrolls out so re-entering re-animates
          entry.target.classList.remove('is-visible');
        }
      });
    }, { threshold: 0.3 });

    cards.forEach(function (card) { observer.observe(card); });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
/* ============================================================
   PROJEKTE (careers board) — renders into #kp-jobs-root on projekte.html.
   Reproduces the look of the previous Black & Grey careers board
   (dark hero + search + filters sidebar + job cards + detail modal),
   Kastell-branded and populated with the current openings below.
   To edit the vacancies, change the JOBS array.
   ============================================================ */
(function () {
  var CONTACT = 'kontakt@kastellpersonalberatung.com';

  // cat: SAP | IT | PMO   (drives filters + generated description blocks)
  var JOBS = [
    { t: 'Manager Consulting SAP Payroll in M&uuml;nchen oder remote (m/w/d)', loc: 'M&uuml;nchen / Remote', remote: true, cat: 'SAP', mod: 'SAP Payroll / HCM', exp: '5+ Jahre', date: '02.07.2026' },
    { t: 'SAP Senior Consultant im Retail-Umfeld remote (m/w/d)', loc: 'Remote', remote: true, cat: 'SAP', mod: 'SAP Retail', exp: '5+ Jahre', date: '30.06.2026' },
    { t: 'Manager Consulting SAP Manufacturing (m/w/d)', loc: 'Deutschland', remote: false, cat: 'SAP', mod: 'SAP Manufacturing (PP/DM)', exp: '5+ Jahre', date: '28.06.2026' },
    { t: 'SAP-Basis Senior Administrator im Rhein-Neckar-Kreis (m/w/d)', loc: 'Rhein-Neckar-Kreis', remote: false, cat: 'SAP', mod: 'SAP Basis', exp: '4-5 Jahre', date: '25.06.2026' },
    { t: 'Senior Inhouse Consultant SAP-CO/PS (m/w/d) im Raum Koblenz', loc: 'Raum Koblenz', remote: false, cat: 'SAP', mod: 'SAP CO / PS', exp: '5+ Jahre', date: '24.06.2026' },
    { t: 'Senior Inhouse Consultant SAP-EWM/LES (m/w/d) im Raum Koblenz', loc: 'Raum Koblenz', remote: false, cat: 'SAP', mod: 'SAP EWM / LES', exp: '5+ Jahre', date: '24.06.2026' },
    { t: '(Senior) Consultant SAP-SuccessFactors (Berlin und remote) (m/w/d)', loc: 'Berlin / Remote', remote: true, cat: 'SAP', mod: 'SAP SuccessFactors', exp: '3-5 Jahre', date: '20.06.2026' },
    { t: 'Inhouse Consultant SAP FI/CO im Kreis Tuttlingen (m/w/d)', loc: 'Kreis Tuttlingen', remote: false, cat: 'SAP', mod: 'SAP FI / CO', exp: '3-5 Jahre', date: '18.06.2026' },
    { t: 'Global Teamlead SAP im Kreis Tuttlingen (m/w/d)', loc: 'Kreis Tuttlingen', remote: false, cat: 'SAP', mod: 'SAP (Teamleitung)', exp: '7+ Jahre', date: '18.06.2026' },
    { t: 'Inhouse Consultant SAP SD/CS im Kreis Tuttlingen (m/w/d)', loc: 'Kreis Tuttlingen', remote: false, cat: 'SAP', mod: 'SAP SD / CS', exp: '3-5 Jahre', date: '16.06.2026' },
    { t: 'Lead Consultant SuccessFactors EC in Frankfurt/Freiburg/K&ouml;ln/Remote (m/w/d)', loc: 'Frankfurt / Freiburg / K&ouml;ln / Remote', remote: true, cat: 'SAP', mod: 'SuccessFactors EC', exp: '5+ Jahre', date: '14.06.2026' },
    { t: 'Inhouse Consultant SAP SuccessFactors in Linz oder remote (m/w/d)', loc: 'Linz / Remote', remote: true, cat: 'SAP', mod: 'SAP SuccessFactors', exp: '3-5 Jahre', date: '12.06.2026' },
    { t: 'Projekt Koordinator (m/w/d) im Projekt Management Office im Ortenau Kreis', loc: 'Ortenau Kreis', remote: false, cat: 'PMO', mod: 'Projekt Management Office', exp: '3-5 Jahre', date: '11.06.2026' },
    { t: 'Fullstack Web Developer in Dresden (m/w/d)', loc: 'Dresden', remote: false, cat: 'IT', mod: 'Fullstack Web Development', exp: '3-5 Jahre', date: '10.06.2026' },
    { t: 'Inhouse Consultant SAP-FS-CD in M&uuml;nchen (m/w/d)', loc: 'M&uuml;nchen', remote: false, cat: 'SAP', mod: 'SAP FS-CD', exp: '3-5 Jahre', date: '08.06.2026' },
    { t: 'SAP-Basis Senior Inhouse Consultant in M&uuml;nchen (m/w/d)', loc: 'M&uuml;nchen', remote: false, cat: 'SAP', mod: 'SAP Basis', exp: '5+ Jahre', date: '05.06.2026' },
    { t: 'SAP-HCM Specialist (m/w/d) im Landkreis Dillingen /Bayern', loc: 'Landkreis Dillingen / Bayern', remote: false, cat: 'SAP', mod: 'SAP HCM', exp: '3-5 Jahre', date: '03.06.2026' }
  ];

  var CATLABEL = { SAP: 'SAP', IT: 'IT / Software', PMO: 'Projektmanagement' };

  var TASKS = {
    SAP: ['Betreuung, Customizing und Weiterentwicklung der SAP-Systemlandschaft im Modul ' + '{mod}' + '.',
      'Analyse und Optimierung der zugrunde liegenden Gesch&auml;ftsprozesse gemeinsam mit den Fachbereichen.',
      'Steuerung von (Teil-)Projekten, Roll-outs und Release-Wechseln.',
      'Second- und Third-Level-Support sowie Schulung der Key-User.'],
    IT: ['Konzeption und Entwicklung moderner Webanwendungen im Frontend und Backend.',
      'Umsetzung neuer Features entlang des gesamten Entwicklungszyklus.',
      'Sicherstellung von Code-Qualit&auml;t, Performance und Wartbarkeit.',
      'Enge Zusammenarbeit mit Produkt und Design in einem agilen Team.'],
    PMO: ['Koordination und Steuerung von Projekten innerhalb des Project Management Office.',
      'Planung und &Uuml;berwachung von Terminen, Ressourcen und Budgets.',
      'Aufbereitung von Reports, Statusberichten und Entscheidungsvorlagen.',
      'Schnittstelle zwischen Projektleitung, Fachbereichen und Management.']
  };
  var PROFILE = {
    SAP: ['Mehrj&auml;hrige Erfahrung im SAP-Umfeld, idealerweise in ' + '{mod}' + '.',
      'Fundiertes Prozessverst&auml;ndnis und Freude an der Arbeit mit Fachbereichen.',
      'Sehr gute Deutsch- und gute Englischkenntnisse.',
      'Strukturierte, eigenverantwortliche und l&ouml;sungsorientierte Arbeitsweise.'],
    IT: ['Einschl&auml;gige Erfahrung in der Softwareentwicklung (Fullstack).',
      'Sicherer Umgang mit modernen Frameworks und sauberem, testbarem Code.',
      'Teamgeist, Neugier und eine l&ouml;sungsorientierte Denkweise.',
      'Sehr gute Deutschkenntnisse.'],
    PMO: ['Erfahrung im Projektmanagement oder in einem PMO.',
      'Sehr gute organisatorische F&auml;higkeiten und ein Blick f&uuml;rs Detail.',
      'Sicherer Umgang mit MS Office und g&auml;ngigen Projekttools.',
      'Ausgepr&auml;gte Kommunikations- und Koordinationsst&auml;rke.']
  };
  var BENEFITS = [
    'Attraktives Gehaltspaket und flexible Arbeitszeiten.',
    'M&ouml;glichkeit zum mobilen Arbeiten bzw. Remote-Anteil.',
    'Individuelle Weiterbildungs- und Entwicklungsm&ouml;glichkeiten.',
    'Ein wertsch&auml;tzendes, kollegiales Umfeld mit flachen Hierarchien.'
  ];

  function bullets(arr, mod) {
    return '<ul>' + arr.map(function (b) {
      return '<li>' + b.replace('{mod}', mod) + '</li>';
    }).join('') + '</ul>';
  }
  function shortText(j) {
    if (j.cat === 'SAP') return 'F&uuml;r unseren Mandanten suchen wir eine:n erfahrene:n Spezialist:in im Bereich ' + j.mod + ' &ndash; mit echtem Gestaltungsspielraum.';
    if (j.cat === 'IT') return 'Werden Sie Teil eines Entwicklungsteams und bauen Sie moderne, nutzerzentrierte Webanwendungen mit.';
    return 'Koordinieren Sie spannende Projekte im PMO und behalten Sie Termine, Budgets und Stakeholder souver&auml;n im Blick.';
  }
  function longText(j) {
    return '<p>F&uuml;r unseren Mandanten &ndash; ein etabliertes Unternehmen &ndash; besetzen wir zum n&auml;chstm&ouml;glichen Zeitpunkt die Position <strong>' + j.t + '</strong>' +
      (j.loc ? ' am Standort ' + j.loc : '') + '. ' + shortText(j) + '</p>' +
      '<h4>Ihre Aufgaben</h4>' + bullets(TASKS[j.cat], j.mod) +
      '<h4>Ihr Profil</h4>' + bullets(PROFILE[j.cat], j.mod) +
      '<h4>Wir bieten</h4>' + bullets(BENEFITS, j.mod);
  }

  var pinIcon = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>';
  var clockIcon = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';

  function boot() {
    var root = document.getElementById('kp-jobs-root');
    if (!root || root.dataset.done) return;
    root.dataset.done = '1';

    // ---- static shell (hero + board skeleton) --------------------------
    root.innerHTML =
      '<section class="kp-hero">' +
      '<div class="kp-hero__inner">' +
      '<p class="kp-hero__eyebrow">Karriere bei Kastell</p>' +
      '<h1 class="kp-hero__title">Schnell. Pr&auml;zise. Vertraulich. Menschlich.</h1>' +
      '<p class="kp-hero__sub">Entdecken Sie ausgew&auml;hlte Positionen in IT, SAP, Engineering und Financial Services &ndash; mit Tempo, Diskretion und ehrlichem Feedback, wenn der Fit stimmt.</p>' +
      '<a href="#kp-openings" class="kp-hero__btn">Stellenangebote ansehen</a>' +
      '</div>' +
      '</section>' +
      '<section class="kp-board" id="kp-openings">' +
      '<div class="kp-board__inner">' +
      '<header class="kp-board__head">' +
      '<h2>Stellenangebote</h2>' +
      '<p class="kp-board__sub">Aktuelle Positionen bei f&uuml;hrenden Unternehmen in Deutschland</p>' +
      '</header>' +
      '<div class="kp-search">' +
      '<div class="kp-search__field"><label>Was</label><input type="text" id="kp-what" placeholder="Jobtitel, Modul, Keyword"></div>' +
      '<div class="kp-search__field"><label>Wo</label><input type="text" id="kp-where" placeholder="Ort oder Region"></div>' +
      '<button type="button" class="kp-search__btn" id="kp-search-btn">Suchen</button>' +
      '</div>' +
      '<div class="kp-layout">' +
      '<aside class="kp-filters">' +
      '<h3>Filter</h3>' +
      '<div class="kp-filter-group"><h4>Anstellung</h4><label class="kp-check"><input type="checkbox" id="kp-remote"> Remote m&ouml;glich</label></div>' +
      '<div class="kp-filter-group"><h4>Bereich</h4><div id="kp-cats"></div></div>' +
      '<button type="button" class="kp-filters__reset" id="kp-reset">Filter zur&uuml;cksetzen</button>' +
      '</aside>' +
      '<div class="kp-main">' +
      '<p class="kp-count" id="kp-count"></p>' +
      '<div class="kp-list" id="kp-list"></div>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '</section>';

    // category checkboxes
    var cats = {};
    JOBS.forEach(function (j) { cats[j.cat] = (cats[j.cat] || 0) + 1; });
    document.getElementById('kp-cats').innerHTML = Object.keys(cats).map(function (c) {
      return '<label class="kp-check"><input type="checkbox" class="kp-cat" value="' + c + '"> ' + CATLABEL[c] + ' (' + cats[c] + ')</label>';
    }).join('');

    var listEl = document.getElementById('kp-list');
    var countEl = document.getElementById('kp-count');
    var whatEl = document.getElementById('kp-what');
    var whereEl = document.getElementById('kp-where');
    var remoteEl = document.getElementById('kp-remote');

    function txt(s) { var d = document.createElement('div'); d.innerHTML = s; return (d.textContent || '').toLowerCase(); }

    function current() {
      var what = txt(whatEl.value), where = txt(whereEl.value);
      var onlyRemote = remoteEl.checked;
      var checkedCats = Array.prototype.map.call(document.querySelectorAll('.kp-cat:checked'), function (c) { return c.value; });
      return JOBS.filter(function (j) {
        if (onlyRemote && !j.remote) return false;
        if (checkedCats.length && checkedCats.indexOf(j.cat) === -1) return false;
        if (what && (txt(j.t) + ' ' + txt(j.mod)).indexOf(what) === -1) return false;
        if (where && txt(j.loc).indexOf(where) === -1) return false;
        return true;
      });
    }

    function render() {
      var rows = current();
      countEl.innerHTML = rows.length + ' offene ' + (rows.length === 1 ? 'Position' : 'Positionen');
      if (!rows.length) {
        listEl.innerHTML = '<div class="kp-empty">Keine Positionen gefunden. Bitte passen Sie Ihre Suche an.</div>';
        return;
      }
      listEl.innerHTML = rows.map(function (j) {
        var idx = JOBS.indexOf(j);
        return '<article class="kp-card" data-i="' + idx + '" tabindex="0" role="button">' +
          '<div class="kp-card__body">' +
          '<h3 class="kp-card__title">' + j.t + '</h3>' +
          '<div class="kp-card__meta">' +
          '<span>' + pinIcon + ' ' + j.loc + '</span>' +
          '<span class="kp-card__exp">' + j.exp + '</span>' +
          (j.remote ? '<span class="kp-tag kp-tag--remote">Remote</span>' : '') +
          '<span class="kp-tag">' + CATLABEL[j.cat] + '</span>' +
          '</div>' +
          '<p class="kp-card__snippet">' + shortText(j) + '</p>' +
          '<div class="kp-card__foot"><span>Vollzeit</span><span class="kp-card__date">' + clockIcon + ' ' + j.date + '</span></div>' +
          '</div>' +
          '<span class="kp-card__cta">Details</span>' +
          '</article>';
      }).join('');
    }

    // ---- detail modal ---------------------------------------------------
    var modal = document.createElement('div');
    modal.className = 'kp-modal';
    modal.innerHTML =
      '<div class="kp-modal__backdrop" data-close></div>' +
      '<div class="kp-modal__panel" role="dialog" aria-modal="true">' +
      '<button class="kp-modal__close" data-close aria-label="Schlie&szlig;en">&times;</button>' +
      '<div class="kp-modal__scroll">' +
      '<p class="kp-modal__eyebrow">Stellenangebot</p>' +
      '<h2 class="kp-modal__title"></h2>' +
      '<div class="kp-modal__meta"></div>' +
      '<div class="kp-modal__body"></div>' +
      '<div class="kp-modal__apply"></div>' +
      '</div>' +
      '</div>';
    document.body.appendChild(modal);

    function openJob(j) {
      modal.querySelector('.kp-modal__title').innerHTML = j.t;
      modal.querySelector('.kp-modal__meta').innerHTML =
        '<span>' + pinIcon + ' ' + j.loc + '</span>' +
        '<span>' + clockIcon + ' Vollzeit</span>' +
        '<span class="kp-tag">' + CATLABEL[j.cat] + '</span>' +
        (j.remote ? '<span class="kp-tag kp-tag--remote">Remote</span>' : '') +
        '<span class="kp-modal__exp">' + j.exp + ' Erfahrung</span>';
      modal.querySelector('.kp-modal__body').innerHTML = longText(j);
      var subj = encodeURIComponent('Bewerbung: ' + (function (s) { var d = document.createElement('div'); d.innerHTML = s; return d.textContent; })(j.t));
      modal.querySelector('.kp-modal__apply').innerHTML =
        '<a class="kp-apply-btn" href="mailto:' + CONTACT + '?subject=' + subj + '">Jetzt bewerben</a>' +
        '<span class="kp-apply-note">Ref.-Kontakt: ' + CONTACT + '</span>';
      modal.querySelector('.kp-modal__scroll').scrollTop = 0;
      modal.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }
    function closeJob() { modal.classList.remove('is-open'); document.body.style.overflow = ''; }

    modal.addEventListener('click', function (e) { if (e.target.hasAttribute('data-close')) closeJob(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeJob(); });

    listEl.addEventListener('click', function (e) {
      var card = e.target.closest('.kp-card'); if (card) openJob(JOBS[+card.dataset.i]);
    });
    listEl.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      var card = e.target.closest('.kp-card'); if (card) { e.preventDefault(); openJob(JOBS[+card.dataset.i]); }
    });

    // ---- wire filters ---------------------------------------------------
    [whatEl, whereEl].forEach(function (el) { el.addEventListener('input', render); });
    document.getElementById('kp-search-btn').addEventListener('click', render);
    remoteEl.addEventListener('change', render);
    document.getElementById('kp-cats').addEventListener('change', render);
    document.getElementById('kp-reset').addEventListener('click', function () {
      whatEl.value = ''; whereEl.value = ''; remoteEl.checked = false;
      Array.prototype.forEach.call(document.querySelectorAll('.kp-cat'), function (c) { c.checked = false; });
      render();
    });

    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  window.addEventListener('load', boot);
})();

/* ============================================================
   SCROLL-SCRUB ENGINE — drives every .kp-scrolly section.
   The section is a tall scroll track; inside it a 100vh sticky
   stage holds a video whose currentTime follows scroll progress
   (smoothed with a lerp), plus [data-step] chapters that fade
   in/out over their own progress window. Immersive, buttery,
   and fully degradable: with JS off or reduced motion the video
   simply sits on its first frame and steps activate on scroll.
   ============================================================ */
(function () {
  function clamp(n, lo, hi) { return n < lo ? lo : n > hi ? hi : n; }

  function initScrolly(root) {
    if (root.dataset.scrollyInit) return;
    root.dataset.scrollyInit = '1';
    var video = root.querySelector('video[data-scrub]');
    var steps = Array.prototype.slice.call(root.querySelectorAll('[data-step]'));
    var bar = root.querySelector('.kp-scrolly__barfill');
    var counter = root.querySelector('[data-step-counter]');

    var duration = 0;
    var targetT = 0;
    var currentT = 0;
    var progress = 0;
    var activeIdx = -1;
    var rafId = null;
    var seekReady = true;

    if (video) {
      video.muted = true;
      video.defaultMuted = true;
      video.playsInline = true;
      video.preload = 'auto';
      try { video.pause(); } catch (e) { }
      var setDur = function () {
        if (isFinite(video.duration) && video.duration > 0) {
          duration = video.duration;
        }
      };
      if (video.readyState >= 1) setDur();
      video.addEventListener('loadedmetadata', setDur);
      // browsers drop pending seeks if a new one lands mid-seek;
      // throttle to one in-flight seek at a time for smoothness
      video.addEventListener('seeked', function () { seekReady = true; });
    }

    function computeProgress() {
      var rect = root.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight;
      var total = rect.height - vh;
      if (total <= 0) return 0;
      return clamp(-rect.top / total, 0, 1);
    }

    function updateSteps() {
      var n = steps.length;
      if (!n) return;
      // each step owns an equal slice of the track, with the video
      // given a small lead-in before step 1 appears
      var idx = clamp(Math.floor(progress * n), 0, n - 1);
      if (idx === activeIdx) return;
      activeIdx = idx;
      steps.forEach(function (el, i) {
        el.classList.toggle('is-active', i === idx);
        el.classList.toggle('is-past', i < idx);
      });
      if (counter) {
        counter.textContent = (idx + 1 < 10 ? '0' : '') + (idx + 1);
      }
    }

    function frame() {
      rafId = null;
      if (video && duration) {
        targetT = progress * Math.max(0, duration - 0.08);
        // lerp toward the target so fast scrolls feel fluid, not jumpy
        currentT += (targetT - currentT) * 0.14;
        if (Math.abs(targetT - currentT) < 0.02) currentT = targetT;
        if (seekReady && Math.abs(video.currentTime - currentT) > 0.033) {
          seekReady = false;
          try { video.currentTime = currentT; } catch (e) { seekReady = true; }
        }
        if (Math.abs(targetT - currentT) > 0.005) schedule();
      }
      if (bar) bar.style.transform = 'scaleX(' + progress + ')';
      updateSteps();
    }

    function schedule() {
      if (rafId === null) rafId = requestAnimationFrame(frame);
    }

    function onScroll() {
      progress = computeProgress();
      schedule();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
  }

  function boot() {
    Array.prototype.forEach.call(
      document.querySelectorAll('.kp-scrolly'),
      initScrolly
    );
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  // late-built sections (e.g. the homepage hero replaces the slider on load)
  window.addEventListener('load', boot);
})();



/* ============================================================
   REVEAL SWEEP — the static WP snapshot bakes the theme's
   scroll-animation *initial* state (opacity:0 / translateY) into
   inline styles, and the theme JS that would animate them in does
   not run offline. Sweep them visible with a gentle transition.
   ============================================================ */
(function () {
  function revealAll() {
    var els = document.querySelectorAll(
      'main .will-change, main [data-custom-animations] [style*="opacity"]'
    );
    Array.prototype.forEach.call(els, function (el) {
      if (el.style.opacity !== '' && parseFloat(el.style.opacity) < 1) {
        el.style.transition = 'opacity .9s ease, transform .9s ease';
        el.style.opacity = '1';
        el.style.transform = 'none';
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', revealAll);
  } else {
    revealAll();
  }
  window.addEventListener('load', revealAll);
  setTimeout(revealAll, 1500);
})();


/* The theme preloader never completes in the static mirror — its classes
   stay on <body> (dragging overflow:hidden along) and its fixed wrap stays
   in the DOM. Clear both. */
(function () {
  function clearPreloader() {
    document.body.classList.remove(
      'lqd-preloader-activated', 'lqd-preloader-animations-started'
    );
    var w = document.querySelector('.lqd-preloader-wrap');
    if (w && w.parentNode) w.parentNode.removeChild(w);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', clearPreloader);
  } else {
    clearPreloader();
  }
})();



/* ============================================================
   ÜBER UNS — GSAP/ScrollTrigger animation layer (the libraries are
   linked only on about-us.html from assets/vendor). Portrait
   parallax, cascading content reveals and stat count-ups. Fully
   degradable: without the libs the page is simply static.
   ============================================================ */
(function () {
  function boot() {
    if (boot.done) return;
    if (!window.gsap || !window.ScrollTrigger) return;
    if (!document.querySelector('.kpa-sticky-team')) return;
    boot.done = true;
    gsap.registerPlugin(ScrollTrigger);
    // late layout shifts (fonts, images) can stale the trigger positions
    window.addEventListener('load', function () {
      setTimeout(function () { ScrollTrigger.refresh(); }, 600);
    });

    // section headers + intro copy drift up as they enter
    gsap.utils.toArray('.kpa-eyebrow, .kpa-title, .kpa-lead').forEach(function (el) {
      gsap.from(el, {
        opacity: 0, y: 36, duration: 1, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true }
      });
    });
    gsap.from('.kpa-insight', {
      opacity: 0, y: 40, duration: 1, ease: 'power3.out', stagger: 0.16,
      scrollTrigger: { trigger: '.kpa-intro-grid', start: 'top 84%', once: true }
    });

    // stats — the numeric ones count up when the band scrolls in
    gsap.utils.toArray('.kpa-stat').forEach(function (stat, i) {
      var numEl = stat.querySelector('.kpa-stat-num');
      var m = numEl && numEl.textContent.trim().match(/^(\d+)(\+?)$/);
      gsap.from(stat, {
        opacity: 0, y: 30, duration: .8, delay: i * .1, ease: 'power2.out',
        scrollTrigger: { trigger: '.kpa-stats', start: 'top 85%', once: true }
      });
      if (m) {
        var target = parseInt(m[1], 10);
        var suffix = m[2] || '';
        var counter = { n: 0 };
        gsap.to(counter, {
          n: target, duration: 1.6, delay: i * .1, ease: 'power1.out',
          scrollTrigger: { trigger: '.kpa-stats', start: 'top 85%', once: true },
          onUpdate: function () { numEl.textContent = Math.round(counter.n) + suffix; }
        });
      }
    });

    // team cards — slow portrait parallax + cascading text reveal
    gsap.utils.toArray('.kpa-sticky-card').forEach(function (card) {
      var imgLeft = !!card.querySelector('.kpa-sticky-card--img-left');
      var img = card.querySelector('.kpa-sticky-card__img img');
      if (img) {
        // drift + straighten as the card travels through the viewport
        gsap.fromTo(img,
          { y: -46, rotation: imgLeft ? -3 : 3, scale: 1.04 },
          {
            y: 46, rotation: imgLeft ? 2 : -2, scale: 1.04, ease: 'none',
            scrollTrigger: { trigger: card, start: 'top bottom', end: 'bottom top', scrub: true }
          });
      }
      var num = card.querySelector('.kpa-sticky-card__eyebrow');
      if (num) {
        gsap.fromTo(num, { yPercent: 26 }, {
          yPercent: -14, ease: 'none',
          scrollTrigger: { trigger: card, start: 'top bottom', end: 'bottom top', scrub: true }
        });
      }
      var items = card.querySelectorAll(
        '.kpa-sticky-card__name, .kpa-sticky-card__role, .kpa-sticky-card__bio p, .kpa-sticky-card__tags span'
      );
      gsap.from(items, {
        opacity: 0, x: imgLeft ? 56 : -56, y: 14, duration: .9, ease: 'power3.out', stagger: 0.09,
        scrollTrigger: { trigger: card, start: 'top 60%', once: true }
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  window.addEventListener('load', boot);
})();



/* Make the careers board reachable: add a "Projekte" item to the main nav
   (the static WP export never carried it) right before the Kontakt pill. */
(function () {
  function addNav() {
    var nav = document.getElementById('primary-nav');
    if (!nav || nav.querySelector('a[href="projekte.html"]')) return;
    var li = document.createElement('li');
    li.className = 'menu-item menu-item-type-post_type menu-item-object-page';
    li.innerHTML = '<a href="projekte.html"><span class="link-icon"></span>' +
      '<span class="link-txt"><span class="link-ext"></span><span class="txt">Projekte</span></span></a>';
    var contact = nav.querySelector('li.contactbtn4');
    nav.insertBefore(li, contact || null);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addNav);
  } else {
    addNav();
  }
})();


/* Homepage: the nav stays out of the way during the immersive hero and
   slides in once the visitor has scrolled through it. */
(function () {
  function boot() {
    if (!document.body.classList.contains('home')) return;
    var shown = false;
    function check() {
      var hero = document.getElementById('kp-hero');
      if (!hero) return;
      var vh = window.innerHeight || 900;
      var show = window.scrollY >= hero.offsetTop + hero.offsetHeight - vh * 1.15;
      if (show !== shown) {
        shown = show;
        document.body.classList.toggle('kp-nav-visible', show);
      }
    }
    window.addEventListener('scroll', check, { passive: true });
    window.addEventListener('resize', check);
    check();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();


/* Staggered rise-in for [data-kp-reveal] elements (service cards etc.) */
(function () {
  function boot() {
    var els = document.querySelectorAll('[data-kp-reveal]');
    if (!els.length || !window.IntersectionObserver) {
      Array.prototype.forEach.call(els, function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = Array.prototype.filter.call(
          el.parentNode.children,
          function (c) { return c.hasAttribute && c.hasAttribute('data-kp-reveal'); }
        );
        var idx = siblings.indexOf(el);
        el.style.transitionDelay = (Math.max(idx, 0) * 90) + 'ms';
        el.classList.add('is-in');
        io.unobserve(el);
      });
    }, { threshold: 0.18 });
    Array.prototype.forEach.call(els, function (el) { io.observe(el); });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
