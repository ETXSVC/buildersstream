// BuildersStream — script.js

// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
const navActions = document.querySelector('.nav-actions');

if (toggle) {
  toggle.addEventListener('click', () => {
    const isOpen = navLinks.style.display === 'flex';
    if (isOpen) {
      navLinks.style.display = '';
      navActions.style.display = '';
      document.body.style.overflow = '';
    } else {
      navLinks.style.cssText = 'display:flex;flex-direction:column;position:fixed;top:64px;left:0;right:0;background:#0e1117;border-bottom:1px solid rgba(255,255,255,0.07);padding:16px 24px;gap:4px;z-index:99';
      navActions.style.cssText = 'display:flex;flex-direction:column;position:fixed;top:auto;left:0;right:0;padding:16px 24px;background:#0e1117;gap:8px;z-index:99;bottom:0;border-top:1px solid rgba(255,255,255,0.07)';
      document.body.style.overflow = 'hidden';
    }
  });
}

// Animate viewer count
function animateCounter(el, target, duration = 1200) {
  const start = performance.now();
  const from = 0;
  const update = (time) => {
    const progress = Math.min((time - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(from + (target - from) * ease).toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

// Intersection observer for stat numbers
const statNums = document.querySelectorAll('.stat-num, .community-num span');
const seen = new Set();

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !seen.has(entry.target)) {
      seen.add(entry.target);
      const text = entry.target.textContent;
      const numMatch = text.match(/[\d,]+/);
      if (numMatch) {
        const num = parseInt(numMatch[0].replace(/,/g, ''));
        const suffix = text.replace(/[\d,]+/, '').trim();
        const el = entry.target;
        const origText = text;
        animateCounter({ set textContent(v) { el.textContent = v.toLocaleString() + suffix; } }, num);
      }
    }
  });
}, { threshold: 0.5 });

statNums.forEach(el => observer.observe(el));

// Simulate live viewer count fluctuation
const viewerEls = document.querySelectorAll('.stream-viewers, .schedule-viewers');
let baseViewers = 1847;

setInterval(() => {
  const delta = Math.floor(Math.random() * 20) - 8;
  baseViewers = Math.max(1800, baseViewers + delta);
  viewerEls.forEach(el => {
    if (el.textContent.includes('watching')) {
      el.innerHTML = el.innerHTML.replace(/[\d,]+(?= watching)/, baseViewers.toLocaleString());
    }
  });
}, 4000);

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const id = link.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Highlight nav on scroll
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a');

const scrollSpy = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navAnchors.forEach(a => a.style.color = '');
      const match = document.querySelector(`.nav-links a[href="#${entry.target.id}"]`);
      if (match) match.style.color = '#e8eaf0';
    }
  });
}, { rootMargin: '-40% 0px -55% 0px' });

sections.forEach(s => scrollSpy.observe(s));
