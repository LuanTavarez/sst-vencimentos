/* Tavarez SST · interações e animações
   GSAP 3.13 via CDN (gsap, ScrollTrigger, SplitText). Se o GSAP não
   carregar ou o visitante pedir menos movimento, a página aparece
   inteira, sem animação. */

// recarregar sempre volta ao topo
if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
const toTop = () => window.scrollTo(0, 0);
toTop();
window.addEventListener('beforeunload', toTop);
window.addEventListener('load', toTop, { once: true });

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const hasGsap = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

/* ---------- links do WhatsApp com mensagem pronta ---------- */
const WA = '5511943825639';
$$('[data-wa]').forEach(a => {
  a.href = `https://wa.me/${WA}?text=${encodeURIComponent(a.dataset.wa)}`;
  a.target = '_blank';
  a.rel = 'noopener';
});
$('#yr').textContent = new Date().getFullYear();

/* ---------- header, progresso e menu ativo ---------- */
const header = $('#top');
const bar = $('#progress');
const navLinks = $$('.nav a');
const sections = navLinks.map(a => $(a.getAttribute('href')));
function onScroll() {
  const y = scrollY;
  header.classList.toggle('scrolled', y > 10);
  const max = document.documentElement.scrollHeight - innerHeight;
  bar.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
  let cur = -1;
  sections.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * .4) cur = i; });
  navLinks.forEach((a, i) => a.classList.toggle('on', i === cur));
}
addEventListener('scroll', onScroll, { passive: true });
onScroll();

/* ---------- painel de vencimentos (demo) ---------- */
const DAY = 864e5;
const today = new Date(); today.setHours(0, 0, 0, 0);
const renewDays = { ASO: 365, Treinamento: 730, Extintor: 365, EPI: 180, Terceiros: 365 };
const items = [
  { n: 'ASO periódico · Carlos M.', c: 'ASO', sub: 'Produção', d: -6 },
  { n: 'NR-35 · Trabalho em altura', c: 'Treinamento', sub: 'Manutenção · 4 pessoas', d: -2 },
  { n: 'Recarga extintor PQS 06', c: 'Extintor', sub: 'Galpão B', d: 9 },
  { n: 'ASO periódico · Juliana R.', c: 'ASO', sub: 'Expedição', d: 14 },
  { n: 'Documentação Empreiteira Alfa', c: 'Terceiros', sub: 'Obra do mezanino', d: -1 },
  { n: 'NR-11 · Empilhadeira', c: 'Treinamento', sub: 'Logística · 3 pessoas', d: 27 },
  { n: 'Cinto paraquedista · lote 12', c: 'EPI', sub: 'Inspeção semestral', d: 22 },
  { n: 'Recarga extintor CO2 02', c: 'Extintor', sub: 'Quadro elétrico', d: 140 },
  { n: 'ASO periódico · Pedro S.', c: 'ASO', sub: 'Administrativo', d: 210 },
  { n: 'Integração Transportadora Beta', c: 'Terceiros', sub: 'Portaria', d: 95 }
].map((it, id) => ({ ...it, id, date: new Date(today.getTime() + it.d * DAY) }));

const cats = ['Todos', 'ASO', 'Treinamento', 'Extintor', 'EPI', 'Terceiros'];
let curCat = 'Todos';
let lastRenewed = null;
const tabs = $('#tabs');
const rows = $('#rows');
const daysLeft = it => Math.round((it.date - today) / DAY);
const status = d => (d < 0 ? 'red' : d <= 30 ? 'amber' : 'green');
const label = d => (d < 0 ? `vencido há ${-d}d` : d === 0 ? 'vence hoje' : d <= 30 ? `vence em ${d}d` : 'em dia');
const fmt = dt => dt.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' });

cats.forEach(c => {
  const b = document.createElement('button');
  b.className = 'tab';
  b.type = 'button';
  b.textContent = c;
  b.setAttribute('aria-pressed', c === curCat);
  b.addEventListener('click', () => {
    curCat = c;
    $$('.tab', tabs).forEach(t => t.setAttribute('aria-pressed', t.textContent === c));
    render(true);
  });
  tabs.appendChild(b);
});

function countTo(el, to, suffix = '') {
  const from = parseInt(el.textContent, 10) || 0;
  if (from === to) return;
  if (!hasGsap || reduce) { el.textContent = to + suffix; return; }
  const o = { v: from };
  gsap.to(o, { v: to, duration: .7, ease: 'power2.out', onUpdate: () => { el.textContent = Math.round(o.v) + suffix; } });
  const box = el.closest('.kpi');
  box.classList.remove('bump'); void box.offsetWidth; box.classList.add('bump');
}

function render(animate, kpis = true) {
  const list = items
    .filter(it => curCat === 'Todos' || it.c === curCat)
    .sort((a, b) => daysLeft(a) - daysLeft(b))
    .slice(0, 6);
  rows.innerHTML = '';
  list.forEach(it => {
    const d = daysLeft(it);
    const s = status(d);
    const r = document.createElement('div');
    r.className = `row s-${s}`;
    r.innerHTML = '<span class="bar"></span><div class="who"><b></b><small></small></div><span class="st"></span><button class="ren" type="button">Renovar</button>';
    $('b', r).textContent = it.n;
    $('small', r).textContent = `${it.c} · ${it.sub} · ${fmt(it.date)}`;
    $('.st', r).textContent = label(d);
    const btn = $('.ren', r);
    btn.setAttribute('aria-label', `Renovar ${it.n}`);
    if (s === 'green') btn.disabled = true;
    btn.addEventListener('click', () => {
      it.date = new Date(today.getTime() + renewDays[it.c] * DAY);
      lastRenewed = it.id;
      render(false);
    });
    if (it.id === lastRenewed) r.classList.add('flash');
    rows.appendChild(r);
  });
  lastRenewed = null;
  if (animate && hasGsap && !reduce) gsap.from(rows.children, { y: 10, opacity: 0, duration: .4, stagger: .05, ease: 'power2.out' });
  if (kpis) updateKpis();
}

function updateKpis() {
  let red = 0, amber = 0;
  items.forEach(it => { const s = status(daysLeft(it)); if (s === 'red') red++; else if (s === 'amber') amber++; });
  const conf = Math.round((items.length - red) / items.length * 100);
  countTo($('#k-red'), red);
  countTo($('#k-amber'), amber);
  countTo($('#k-conf'), conf, '%');
  $('#k-meter').style.width = conf + '%';
}

// linhas já entram no DOM agora, para o hero nascer com a altura final
// (os números dos KPIs só contam quando o painel aparece)
render(false, false);

/* ---------- quiz ---------- */
const qs = $$('#quiz .q');
const dots = $$('#qdots i');
let score = 0;
const msgs = [
  'Normal: quase todo mundo erra essas. É por isso que treinamento precisa prender a atenção.',
  'Tem coisa aí que muita empresa ainda faz errado. Um treinamento que prende resolve.',
  'Quase lá! Agora imagina a sua equipe jogando isso no celular, com a cara da sua empresa.',
  'Gabaritou! Agora imagina a sua equipe jogando isso no celular, com a cara da sua empresa.'
];
qs.forEach((q, i) => {
  $$('.opts button', q).forEach(b => b.addEventListener('click', () => {
    if (q.classList.contains('done')) return;
    const right = b.dataset.v === q.dataset.a;
    if (right) score++;
    $$('.opts button', q).forEach(x => { if (x.dataset.v === q.dataset.a) x.classList.add('ok'); });
    if (!right) b.classList.add('no');
    dots[i].classList.add(right ? 'ok' : 'no');
    q.classList.add('done');
    if (hasGsap && !reduce) gsap.from($('.ans', q), { y: 8, opacity: 0, duration: .35, ease: 'power2.out' });
  }));
  $('.next', q).addEventListener('click', () => {
    q.classList.remove('on');
    const next = qs[i + 1] || $('#qend');
    if (!qs[i + 1]) {
      $('#qbig').textContent = `${score}/3`;
      $('#qmsg').textContent = msgs[score];
    }
    next.classList.add('on');
    if (hasGsap && !reduce) {
      gsap.from(next, { x: 24, opacity: 0, duration: .4, ease: 'power3.out' });
      if (!qs[i + 1]) gsap.from('.qe-hat', { y: -60, rotation: -30, duration: .8, ease: 'bounce.out' });
    }
  });
});
$('#qagain').addEventListener('click', () => {
  score = 0;
  dots.forEach(d => d.className = '');
  qs.forEach(q => { q.classList.remove('done', 'on'); $$('.opts button', q).forEach(b => b.className = ''); });
  $('#qend').classList.remove('on');
  qs[0].classList.add('on');
});

/* ---------- QR decorativo do crachá ---------- */
(() => {
  const qr = $('#qr');
  const isFinder = (x, y) => (x < 3 && y < 3) || (x > 3 && y < 3) || (x < 3 && y > 3);
  for (let k = 0; k < 49; k++) {
    const x = k % 7, y = Math.floor(k / 7);
    const c = document.createElement('i');
    const on = isFinder(x, y) || (k * 7 + 3) % 5 < 3;
    if (!on) c.className = 'o';
    qr.appendChild(c);
  }
})();

/* ---------- brilho que segue o mouse nos cartões ---------- */
if (finePointer) {
  $$('.glow').forEach(card => card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', `${e.clientX - r.left}px`);
    card.style.setProperty('--my', `${e.clientY - r.top}px`);
  }));
}

/* ---------- crachá inclina com o mouse ---------- */
const badge = $('#card-id');
if (finePointer && !reduce) {
  const wrap = badge.parentElement;
  wrap.addEventListener('pointermove', e => {
    const r = badge.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - .5;
    const py = (e.clientY - r.top) / r.height - .5;
    badge.style.transform = `rotateY(${px * 16}deg) rotateX(${-py * 10}deg)`;
    badge.style.setProperty('--sx', `${50 + px * 120}%`);
  });
  wrap.addEventListener('pointerleave', () => { badge.style.transform = ''; badge.style.setProperty('--sx', '100%'); });
}

/* ---------- FAQ: abre e fecha suave, um por vez ---------- */
$$('.faq details').forEach(d => {
  const sum = $('summary', d);
  const body = $('.fa', d);
  sum.addEventListener('click', e => {
    if (!hasGsap || reduce) return;
    e.preventDefault();
    if (d.open) {
      gsap.to(body, { height: 0, duration: .35, ease: 'power2.inOut', onComplete: () => { d.open = false; body.style.height = ''; } });
    } else {
      $$('.faq details[open]').forEach(o => { if (o !== d) $('summary', o).click(); });
      d.open = true;
      gsap.fromTo(body, { height: 0 }, { height: 'auto', duration: .45, ease: 'power3.out', clearProps: 'height' });
    }
  });
});

/* ---------- animações ---------- */
function showAll() {
  window.__animOk = true;
  document.documentElement.classList.add('no-anim');
  updateKpis();
}

if (!hasGsap || reduce) {
  showAll();
} else {
  const plugins = [ScrollTrigger];
  if (window.SplitText) plugins.push(SplitText);
  gsap.registerPlugin(...plugins);
  ScrollTrigger.clearScrollMemory('manual');
  gsap.defaults({ ease: 'power3.out' });
  window.__animOk = true;

  document.fonts.ready.then(() => {
    const canSplit = !!window.SplitText;

    /* entrada do hero */
    const tl = gsap.timeline({ delay: .1 });
    const h1 = $('#h1');
    if (canSplit) {
      const split = SplitText.create(h1, { type: 'lines', mask: 'lines' });
      gsap.set(h1, { visibility: 'visible' });
      tl.from(split.lines, { yPercent: 110, duration: 1, stagger: .12, ease: 'power4.out', onComplete: () => split.revert() });
    } else {
      tl.fromTo(h1, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: .9 });
    }
    tl.fromTo('.hero h1 em', { '--ul': 0 }, { '--ul': 1, duration: .8, ease: 'power2.inOut' }, '-=.3')
      .fromTo('.hero-copy .h-in', { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .8, stagger: .08 }, .25)
      .fromTo('.hero-board', { y: 50, opacity: 0, rotateX: 8 }, { y: 0, opacity: 1, rotateX: 0, duration: 1.1, transformPerspective: 1200 }, .35)
      .from('#rows .row', { y: 10, opacity: 0, duration: .4, stagger: .05, ease: 'power2.out' }, .7)
      .add(updateKpis, .7)
      .from('.hero .float', { scale: .4, opacity: 0, duration: 1, stagger: .15, ease: 'back.out(1.6)' }, .6);

    /* títulos das seções entram em linhas */
    $$('.split').forEach(title => {
      if (!canSplit) {
        gsap.fromTo(title, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: .8, scrollTrigger: { trigger: title, start: 'top 85%', once: true } });
        return;
      }
      let done = false;
      gsap.set(title, { visibility: 'visible' });
      SplitText.create(title, {
        type: 'lines', mask: 'lines', autoSplit: true,
        onSplit(self) {
          if (done) return;
          return gsap.from(self.lines, {
            yPercent: 105, duration: .9, stagger: .1, ease: 'power4.out',
            scrollTrigger: { trigger: title, start: 'top 85%', once: true },
            onComplete() { done = true; self.revert(); }
          });
        }
      });
    });

    /* blocos aparecem ao rolar */
    gsap.set('.rv', { y: 28, opacity: 0 });
    ScrollTrigger.batch('.rv', {
      start: 'top 88%',
      once: true,
      onEnter: batch => gsap.to(batch, { y: 0, opacity: 1, duration: .8, stagger: .08, overwrite: true })
    });

    /* fundo do hero e objetos com parallax */
    gsap.to('.hero-bg img', { yPercent: 12, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    $$('.float').forEach((el, i) => {
      const speed = parseFloat(el.dataset.speed) || 40;
      gsap.to(el, { y: speed * 2, rotation: `+=${speed > 0 ? 14 : -14}`, ease: 'none', scrollTrigger: { trigger: el.closest('section'), start: 'top bottom', end: 'bottom top', scrub: 1 } });
      gsap.to(el, { yPercent: 8, duration: 2.6 + i * .3, ease: 'sine.inOut', repeat: -1, yoyo: true });
    });
    gsap.fromTo('.faq-cone', { rotation: -24 }, { rotation: 4, ease: 'none', scrollTrigger: { trigger: '#duvidas', start: 'top bottom', end: 'bottom top', scrub: 1 } });

    /* linha do tempo do ASO preenche */
    gsap.fromTo('#tl-fill', { '--tl': 0 }, { '--tl': 1, ease: 'none', scrollTrigger: { trigger: '#tl', start: 'top 85%', end: 'top 45%', scrub: .6 } });

    /* passos: linha laranja e números acendem */
    const stepEls = $$('.step');
    const vertical = () => innerWidth <= 900;
    gsap.fromTo('#steps-fill', { '--st': 0 }, {
      '--st': 1, ease: 'none',
      scrollTrigger: {
        trigger: '#steps', start: 'top 80%', end: () => (vertical() ? 'bottom 60%' : 'top 35%'), scrub: .6, invalidateOnRefresh: true,
        onUpdate: self => stepEls.forEach((s, i) => s.classList.toggle('on', self.progress >= i / stepEls.length + .01 || (i === 0 && self.progress > 0)))
      }
    });
    gsap.from(stepEls, { y: 30, opacity: 0, duration: .8, stagger: .12, scrollTrigger: { trigger: '#steps', start: 'top 85%', once: true } });

    /* imagem do treinamento */
    gsap.to('.train-img img', { scale: 1, yPercent: -4, ease: 'none', scrollTrigger: { trigger: '.train-img', start: 'top bottom', end: 'bottom top', scrub: true } });

    /* crachá balança ao entrar */
    gsap.from(badge, { rotation: -8, y: -40, duration: 1.6, ease: 'elastic.out(1, .45)', scrollTrigger: { trigger: '#sobre', start: 'top 75%', once: true } });

    /* fita das NRs acelera com a rolagem */
    const skew = gsap.quickTo('.tape span', 'skewX', { duration: .4, ease: 'power3' });
    ScrollTrigger.create({ onUpdate: self => skew(gsap.utils.clamp(-6, 6, self.getVelocity() / -300)) });

    ScrollTrigger.refresh();
  });
}
