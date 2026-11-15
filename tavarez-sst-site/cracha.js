/* Crachá 3D da seção "Sobre".
   Desenha a frente, o verso e a fita do crachá num canvas (com as fontes
   do site) e entrega para o lanyard.js. Só monta quando a seção chega
   perto da tela. Se o WebGL não existir, fica o crachá em HTML. */

import { mountLanyard } from './lanyard.js?v=1';

const W = 1024;
const H = Math.round(W * 2.25 / 1.6); // mesma proporção do cartão 3D (1.6 x 2.25)
const C = {
  navy: '#0d141b', panel: '#16212c', line: '#26343f', card: '#f4f1ec', ink: '#141c24',
  muted: '#5d6a75', orange: '#f5841f', green: '#2e9e5b', greenText: '#1f8a4c'
};

const wrap = document.getElementById('badge-wrap');
const box = document.getElementById('lanyard');

function loadImg(src) {
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null);
    img.src = src;
  });
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function hazard(ctx, x, y, w, h, a = C.orange, b = C.navy, step = 28) {
  ctx.save();
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.clip();
  ctx.fillStyle = b;
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = a;
  for (let i = -h; i < w + h; i += step * 2) {
    ctx.beginPath();
    ctx.moveTo(x + i, y + h);
    ctx.lineTo(x + i + h, y);
    ctx.lineTo(x + i + h + step, y);
    ctx.lineTo(x + i + step, y + h);
    ctx.fill();
  }
  ctx.restore();
}

function logo(ctx, x, y, s) {
  const k = s / 64;
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(k, k);
  roundRect(ctx, 0, 0, 64, 64, 15);
  ctx.fillStyle = C.panel;
  ctx.fill();
  ctx.fillStyle = C.orange;
  roundRect(ctx, 13, 14, 38, 10, 2); ctx.fill();
  ctx.fillStyle = '#fff';
  roundRect(ctx, 23, 24, 10, 27, 2); ctx.fill();
  ctx.fillStyle = C.green;
  ctx.beginPath(); ctx.moveTo(51, 35); ctx.lineTo(51, 51); ctx.lineTo(35, 51); ctx.closePath(); ctx.fill();
  ctx.restore();
}

// QR decorativo (não leva a lugar nenhum), com os três quadrados de canto
function qr(ctx, x, y, size, seed = 7) {
  const n = 21;
  const c = size / n;
  let st = seed;
  const rnd = () => ((st = (st * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
  ctx.fillStyle = '#fff';
  ctx.fillRect(x - c, y - c, size + c * 2, size + c * 2);
  ctx.fillStyle = C.ink;
  const finder = (fx, fy) => {
    ctx.fillRect(x + fx * c, y + fy * c, 7 * c, 7 * c);
    ctx.fillStyle = '#fff';
    ctx.fillRect(x + (fx + 1) * c, y + (fy + 1) * c, 5 * c, 5 * c);
    ctx.fillStyle = C.ink;
    ctx.fillRect(x + (fx + 2) * c, y + (fy + 2) * c, 3 * c, 3 * c);
  };
  for (let j = 0; j < n; j++) {
    for (let i = 0; i < n; i++) {
      const inFinder = (i < 8 && j < 8) || (i > 12 && j < 8) || (i < 8 && j > 12);
      if (!inFinder && rnd() > .52) ctx.fillRect(x + i * c, y + j * c, c, c);
    }
  }
  finder(0, 0); finder(14, 0); finder(0, 14);
}

function text(ctx, str, x, y, font, color, align = 'left', spacing = 0) {
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'alphabetic';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${spacing}px`;
  ctx.fillText(str, x, y);
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
}

function drawFront(avatar) {
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');

  ctx.fillStyle = C.card;
  ctx.fillRect(0, 0, W, H);

  // faixa superior azul-noite (o furo do cordão fica aqui)
  ctx.fillStyle = C.navy;
  ctx.fillRect(0, 0, W, 300);
  hazard(ctx, 0, 300, W, 26);
  logo(ctx, 96, 156, 96);
  text(ctx, 'TAVAREZ SST', 216, 222, '800 84px "Barlow Condensed"', '#ffffff', 'left', 2);
  text(ctx, 'SEGURANÇA DO TRABALHO', 220, 262, '500 24px "JetBrains Mono"', '#97a6b3', 'left', 5);

  // foto
  const px = 232, py = 392, ps = 560;
  ctx.save();
  roundRect(ctx, px - 10, py - 10, ps + 20, ps + 20, 44);
  ctx.fillStyle = C.orange;
  ctx.fill();
  roundRect(ctx, px, py, ps, ps, 36);
  ctx.clip();
  if (avatar) {
    const s = Math.max(ps / avatar.width, ps / avatar.height);
    ctx.drawImage(avatar, px + (ps - avatar.width * s) / 2, py + (ps - avatar.height * s) / 2, avatar.width * s, avatar.height * s);
  } else {
    ctx.fillStyle = C.panel;
    ctx.fillRect(px, py, ps, ps);
    logo(ctx, px + ps / 2 - 120, py + ps / 2 - 120, 240);
  }
  ctx.restore();

  // nome e função
  text(ctx, 'LUAN TAVAREZ', W / 2, 1060, '800 104px "Barlow Condensed"', C.ink, 'center', 1);
  text(ctx, 'Técnico em Segurança do Trabalho', W / 2, 1112, '600 34px "Inter"', C.muted, 'center');

  // rodapé do crachá
  ctx.strokeStyle = '#cfc8bd';
  ctx.lineWidth = 3;
  ctx.setLineDash([12, 10]);
  ctx.beginPath(); ctx.moveTo(80, 1160); ctx.lineTo(W - 80, 1160); ctx.stroke();
  ctx.setLineDash([]);
  text(ctx, 'SITUAÇÃO', 84, 1222, '500 24px "JetBrains Mono"', C.muted, 'left', 4);
  ctx.fillStyle = C.green;
  ctx.beginPath(); ctx.arc(98, 1262, 13, 0, Math.PI * 2); ctx.fill();
  text(ctx, 'EM DIA', 124, 1278, '800 50px "Barlow Condensed"', C.greenText, 'left', 1);
  text(ctx, 'ID TVZ-SST-001', 84, 1330, '500 22px "JetBrains Mono"', C.muted, 'left', 3);
  qr(ctx, W - 84 - 150, 1196, 150);

  hazard(ctx, 0, H - 26, W, 26);
  return cv.toDataURL('image/png');
}

function drawBack() {
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = C.navy;
  ctx.fillRect(0, 0, W, H);
  // grade técnica de fundo
  ctx.strokeStyle = 'rgba(255,255,255,.05)';
  ctx.lineWidth = 2;
  for (let x = 0; x < W; x += 64) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 64) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  hazard(ctx, 0, 300, W, 26);

  logo(ctx, W / 2 - 110, 420, 220);
  text(ctx, 'SEGURANÇA DO', W / 2, 800, '800 112px "Barlow Condensed"', '#ffffff', 'center', 1);
  text(ctx, 'TRABALHO QUE', W / 2, 905, '800 112px "Barlow Condensed"', '#ffffff', 'center', 1);
  text(ctx, 'SAI DO PAPEL.', W / 2, 1010, '800 112px "Barlow Condensed"', C.orange, 'center', 1);
  text(ctx, '(11) 94382-5639', W / 2, 1150, '600 40px "Inter"', '#eaf0f4', 'center');
  text(ctx, '@TAVAREZ.SST', W / 2, 1206, '500 28px "JetBrains Mono"', '#97a6b3', 'center', 6);
  text(ctx, 'GUARULHOS · GRANDE SP · TODO O BRASIL', W / 2, 1300, '500 22px "JetBrains Mono"', '#6b7b88', 'center', 3);
  hazard(ctx, 0, H - 26, W, 26);
  return cv.toDataURL('image/png');
}

// fita: imagem deitada (comprimento x largura); o lanyard.js gira e repete
function drawStrap() {
  const cv = document.createElement('canvas');
  cv.width = 1200; cv.height = 192;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = C.orange;
  ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.fillStyle = 'rgba(0,0,0,.06)';
  for (let y = 0; y < cv.height; y += 6) ctx.fillRect(0, y, cv.width, 2);
  ctx.fillStyle = 'rgba(20,11,2,.35)';
  ctx.fillRect(0, 14, cv.width, 4);
  ctx.fillRect(0, cv.height - 18, cv.width, 4);
  for (let k = 0; k < 2; k++) {
    const x0 = k * 600;
    text(ctx, 'TAVAREZ SST', x0 + 60, 124, '800 76px "Barlow Condensed"', '#140b02', 'left', 6);
    hazard(ctx, x0 + 430, 70, 120, 52, '#140b02', C.orange, 14);
  }
  return cv.toDataURL('image/png');
}

async function mount() {
  try {
    await Promise.all([
      document.fonts.load('800 80px "Barlow Condensed"'),
      document.fonts.load('600 30px "Inter"'),
      document.fonts.load('500 24px "JetBrains Mono"')
    ]);
  } catch { /* segue com a fonte que tiver */ }
  const avatar = await loadImg('assets/img/avatar-cracha.webp');
  const small = innerWidth < 700;
  const destroy = mountLanyard(box, {
    frontImage: drawFront(avatar),
    backImage: drawBack(),
    strapImage: drawStrap(),
    cardColor: C.card,
    finish: 'glossy',
    cornerRadius: 0.35,
    size: small ? 0.62 : 0.7,
    strapLength: 0.36,
    strapColor: C.orange,
    strapWidth: 0.7,
    metal: 'silver',
    gravity: 1,
    damping: 0.5,
    elasticity: 0.55,
    breeze: 0.45,
    interactive: true,
    intro: true
  });
  if (destroy) wrap.classList.add('has-lanyard');
}

if (wrap && box) {
  const io = new IntersectionObserver(entries => {
    if (!entries.some(e => e.isIntersecting)) return;
    io.disconnect();
    mount();
  }, { rootMargin: '0px 0px -15% 0px' });
  io.observe(wrap);
}
