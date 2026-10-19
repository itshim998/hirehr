/**
 * HireHR Services - Main Script
 * Vanilla JavaScript | No framework / No external dependencies
 */

// ==========================================================================
// CONFIGURATION
// ==========================================================================
/**
 * FORM SUBMISSION DESTINATION
 * Set this to your designated form handling URL (e.g., Formspree, Formkeep, custom API endpoint).
 * Configured for Cloudflare Workers backend endpoint.
 * If null, the fallback status message is presented to the user upon submission.
 */
const FORM_ENDPOINT = '/api/contact';

/**
 * CLOUDFLARE TURNSTILE CONFIGURATION
 * Test sitekey that always passes: 1x00000000000000000000AA
 * Replace with production sitekey created in Cloudflare dashboard
 */
const TURNSTILE_SITE_KEY = '0x4AAAAAAFYJ5FLwmd03vH67';

// Global Turnstile state & onload handler for explicit rendering
let turnstileWidgetId = null;
let turnstileToken = null;
let turnstileLoadFailed = false;

window.onTurnstileLoad = function() {
  initTurnstile();
};

function initTurnstile() {
  const container = document.getElementById('turnstile-widget');
  if (!container || !window.turnstile) return;
  if (turnstileWidgetId !== null) return;

  try {
    turnstileWidgetId = window.turnstile.render(container, {
      sitekey: TURNSTILE_SITE_KEY,
      theme: 'light',
      callback: function(token) {
        turnstileToken = token;
      },
      'expired-callback': function() {
        turnstileToken = null;
      },
      'error-callback': function() {
        turnstileToken = null;
        turnstileLoadFailed = true;
      }
    });
  } catch (err) {
    turnstileLoadFailed = true;
  }
}

// ==========================================================================
// 1. MOBILE NAVIGATION TOGGLE & ACCESSIBLE DROPDOWNS
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Turnstile if API script already loaded
  initTurnstile();

  const navToggle = document.querySelector('.nav-toggle');
  const mainNav = document.querySelector('.main-navigation');
  const dropdownParents = document.querySelectorAll('.has-dropdown');

  function closeMobileNav() {
    if (!mainNav || !navToggle) return;
    mainNav.classList.remove('is-active');
    navToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-open');
    document.body.style.overflow = '';
  }

  function openMobileNav() {
    if (!mainNav || !navToggle) return;
    mainNav.classList.add('is-active');
    navToggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('nav-open');
    document.body.style.overflow = 'hidden';
  }

  if (navToggle && mainNav) {
    // Stagger indices for mobile overlay items
    const navItems = mainNav.querySelectorAll('.nav-item');
    navItems.forEach((item, idx) => {
      item.style.setProperty('--nav-idx', idx);
    });

    navToggle.addEventListener('click', () => {
      const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
      if (isExpanded) {
        closeMobileNav();
      } else {
        openMobileNav();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mainNav.classList.contains('is-active')) {
        closeMobileNav();
        navToggle.focus();
      }
    });

    // Close mobile nav when clicking normal links
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (link.getAttribute('href') !== '#' && mainNav.classList.contains('is-active')) {
          closeMobileNav();
        }
      });
    });
  }

  // Mobile / keyboard handling for dropdown menus (<1024px accordion)
  dropdownParents.forEach(item => {
    const link = item.querySelector('.nav-link');
    if (link) {
      link.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
          e.preventDefault();
          const isOpen = item.classList.contains('is-open');
          // Close other open dropdowns
          dropdownParents.forEach(other => {
            if (other !== item) {
              other.classList.remove('is-open');
              const otherLink = other.querySelector('.nav-link');
              if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
            }
          });
          item.classList.toggle('is-open', !isOpen);
          link.setAttribute('aria-expanded', !isOpen);
        }
      });
    }
  });

  // ==========================================================================
  // 2. HERO SLIDER IMPLEMENTATION
  // ==========================================================================
  const SLIDE_DURATION = 4000;
  const sliderTrack = document.querySelector('.slider-track');
  const slides = document.querySelectorAll('.slider-slide');
  const bgItems = document.querySelectorAll('.hero-bg-item');
  const prevBtn = document.querySelector('.slider-prev');
  const nextBtn = document.querySelector('.slider-next');
  const dotsContainer = document.querySelector('.slider-dots');
  const sliderSection = document.querySelector('.hero-slider-section');

  if (sliderSection) {
    sliderSection.style.setProperty('--slide-duration', `${SLIDE_DURATION}ms`);
  }

  if (slides.length > 1) {
    let currentSlide = 0;
    const totalSlides = slides.length;
    let autoplayTimer = null;
    let isPaused = false;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function setPaused(paused) {
      isPaused = paused;
      if (sliderSection) {
        sliderSection.classList.toggle('is-paused', paused);
      }
    }

    // Create pagination progress lines
    if (dotsContainer) {
      dotsContainer.innerHTML = '';
      slides.forEach((_, idx) => {
        const dot = document.createElement('button');
        dot.className = `slider-dot ${idx === 0 ? 'is-active' : ''}`;
        dot.setAttribute('aria-label', `Go to slide ${idx + 1}`);
        dot.addEventListener('click', () => {
          goToSlide(idx);
          restartAutoplay();
        });
        dotsContainer.appendChild(dot);
      });
    }

    const updateDots = () => {
      if (!dotsContainer) return;
      const dots = dotsContainer.querySelectorAll('.slider-dot');
      dots.forEach((dot, idx) => {
        const isActive = idx === currentSlide;
        dot.classList.remove('is-active');
        if (isActive) {
          // Force reflow so CSS progress animation cleanly restarts
          void dot.offsetWidth;
          dot.classList.add('is-active');
        }
      });
    };

    const goToSlide = (index) => {
      slides[currentSlide].classList.remove('is-active');
      if (bgItems[currentSlide]) {
        bgItems[currentSlide].classList.remove('is-active');
      }
      currentSlide = (index + totalSlides) % totalSlides;
      slides[currentSlide].classList.add('is-active');
      if (bgItems[currentSlide]) {
        const img = bgItems[currentSlide].querySelector('img');
        if (img) void img.offsetWidth;
        bgItems[currentSlide].classList.add('is-active');
      }
      updateDots();
    };

    const nextSlide = () => goToSlide(currentSlide + 1);
    const prevSlide = () => goToSlide(currentSlide - 1);

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        nextSlide();
        restartAutoplay();
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        prevSlide();
        restartAutoplay();
      });
    }

    // Autoplay logic (4000ms autoplay interval per specification)
    const startAutoplay = () => {
      if (prefersReducedMotion) return;
      stopAutoplay();
      autoplayTimer = setInterval(() => {
        if (!isPaused) {
          nextSlide();
        }
      }, SLIDE_DURATION);
    };

    const stopAutoplay = () => {
      if (autoplayTimer) {
        clearInterval(autoplayTimer);
        autoplayTimer = null;
      }
    };

    const restartAutoplay = () => {
      stopAutoplay();
      startAutoplay();
    };

    // Pause on hover or focus
    if (sliderSection) {
      sliderSection.addEventListener('mouseenter', () => { setPaused(true); });
      sliderSection.addEventListener('mouseleave', () => { setPaused(false); });
      sliderSection.addEventListener('focusin', () => { setPaused(true); });
      sliderSection.addEventListener('focusout', () => { setPaused(false); });
      sliderSection.addEventListener('touchstart', () => { setPaused(true); }, { passive: true });
      sliderSection.addEventListener('touchend', () => { setPaused(false); }, { passive: true });
    }

    startAutoplay();
  }

  // ==========================================================================
  // 3. POPULATE COUNTRY CODE DROPDOWN
  // ==========================================================================
  const countrySelect = document.getElementById('form-country');
  if (countrySelect && window.COUNTRY_DATA) {
    countrySelect.innerHTML = '';
    window.COUNTRY_DATA.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.dial;
      opt.textContent = `${c.name} (${c.dial})`;
      // Default to United States (+1) as in the original WPForms setup
      if (c.code === 'US') {
        opt.selected = true;
      }
      countrySelect.appendChild(opt);
    });
  }

  // ==========================================================================
  // 4. CONSULTATION FORM VALIDATION & HANDLING
  // ==========================================================================
  const consultationForm = document.getElementById('consultation-form');
  const formStatus = document.getElementById('form-status');

  if (consultationForm) {
    consultationForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!formStatus) return;
      formStatus.className = 'form-status';
      formStatus.textContent = '';

      // Collect field values
      const name = (document.getElementById('form-name')?.value || '').trim();
      const company = (document.getElementById('form-company')?.value || '').trim();
      const countryCode = document.getElementById('form-country')?.value || '+1';
      const phone = (document.getElementById('form-phone')?.value || '').trim();
      const email = (document.getElementById('form-email')?.value || '').trim();
      const message = (document.getElementById('form-message')?.value || '').trim();
      const website = (document.getElementById('form-website')?.value || '').trim();

      // Client-side validations
      if (!name) {
        showStatus('error', 'Please enter your Name.');
        document.getElementById('form-name')?.focus();
        return;
      }

      if (!phone) {
        showStatus('error', 'Please enter your Phone Number.');
        document.getElementById('form-phone')?.focus();
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        showStatus('error', 'Please enter a valid Email address.');
        document.getElementById('form-email')?.focus();
        return;
      }

      if (!message) {
        showStatus('error', 'Please enter your Message.');
        document.getElementById('form-message')?.focus();
        return;
      }

      // Check configured destination
      if (!FORM_ENDPOINT) {
        showStatus('info', 'Thank you. Your request inputs have been validated successfully. Note: Form submission endpoint is not yet configured by the site administrator (FORM_ENDPOINT = null in js/main.js), so no external transmission was made.');
        return;
      }

      // Turnstile verification token check
      let activeToken = turnstileToken;
      if (!activeToken && window.turnstile && turnstileWidgetId !== null) {
        try {
          activeToken = window.turnstile.getResponse(turnstileWidgetId);
        } catch {}
      }

      if (!activeToken) {
        if (turnstileLoadFailed || !window.turnstile) {
          showStatus('error', 'Security verification failed to load. Please check your connection or disable ad-blockers and try again.');
        } else {
          showStatus('error', 'Please complete the security verification before submitting.');
        }
        return;
      }

      // If FORM_ENDPOINT is configured:
      const submitBtn = consultationForm.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.textContent : 'Submit';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
      }

      try {
        const payload = {
          name,
          company,
          phone: `${countryCode} ${phone}`,
          email,
          message,
          website,
          turnstileToken: activeToken
        };

        const response = await fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        let responseData = null;
        try {
          responseData = await response.json();
        } catch {}

        if (response.ok && responseData && responseData.ok) {
          if (responseData.delivered === false) {
            // Neutral staging notice when email delivery is not yet configured (Stage A log mode)
            showStatus('info', 'Thank you! Your consultation request has been received (staging notice: email delivery is not yet configured).');
          } else {
            showStatus('success', 'Thank you! Your consultation request has been sent successfully.');
          }
          consultationForm.reset();
        } else {
          showStatus('error', 'There was an issue submitting your request. Please try again or reach out directly via email.');
        }
      } catch (err) {
        showStatus('error', 'Network error encountered while sending request. Please contact us via email.');
      } finally {
        // Reset Turnstile widget after each submit attempt
        if (window.turnstile && turnstileWidgetId !== null) {
          try {
            window.turnstile.reset(turnstileWidgetId);
          } catch {}
        }
        turnstileToken = null;

        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      }
    });
  }

  function showStatus(type, message) {
    if (!formStatus) return;
    formStatus.className = `form-status is-visible ${type}`;
    formStatus.textContent = message;
    formStatus.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
});

