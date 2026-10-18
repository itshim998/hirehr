/**
 * HireHR Services - UI & Motion Infrastructure
 * Size budget: < 4 KB | Vanilla JS | Self-contained
 */
(function() {
  'use strict';

  // 1. Header Scroll State (rAF-throttled, passive)
  var header = document.querySelector('.site-header');
  var ticking = false;

  function updateHeaderScroll() {
    if (!header) return;
    var scrolled = window.scrollY > 24;
    header.classList.toggle('is-scrolled', scrolled);
    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(updateHeaderScroll);
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  updateHeaderScroll();

  // 2. Reveal-on-scroll with IntersectionObserver
  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initReveal() {
    var revealElements = document.querySelectorAll('[data-reveal]');
    if (!revealElements.length) return;

    if (prefersReduced || !('IntersectionObserver' in window)) {
      revealElements.forEach(function(el) {
        el.classList.add('is-revealed');
      });
      return;
    }

    // Assign stagger indices to siblings with data-reveal
    var parentMap = new Map();
    revealElements.forEach(function(el) {
      var parent = el.parentElement || document.body;
      if (!parentMap.has(parent)) {
        parentMap.set(parent, []);
      }
      parentMap.get(parent).push(el);
    });

    parentMap.forEach(function(children) {
      children.forEach(function(child, idx) {
        child.style.setProperty('--reveal-index', Math.min(idx, 5));
      });
    });

    // Mark html as ready for reveal animations (graceful fallback if script blocked)
    document.documentElement.classList.add('has-reveal');

    var observer = new IntersectionObserver(function(entries, obs) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          obs.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.15,
      rootMargin: '0px 0px -40px 0px'
    });

    var vh = window.innerHeight || document.documentElement.clientHeight;
    revealElements.forEach(function(el) {
      var rect = el.getBoundingClientRect();
      // If already above the fold, reveal immediately
      if (rect.top < vh && rect.bottom > 0) {
        el.classList.add('is-revealed');
      } else {
        observer.observe(el);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReveal);
  } else {
    initReveal();
  }
})();
