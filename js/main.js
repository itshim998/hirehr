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
 * Per project rules, this is NOT invented or assumed. If null, a clear non-misleading
 * status message is presented to the user upon submission.
 */
const FORM_ENDPOINT = null;

// ==========================================================================
// 1. MOBILE NAVIGATION TOGGLE & ACCESSIBLE DROPDOWNS
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('.nav-toggle');
  const mainNav = document.querySelector('.main-navigation');
  const dropdownParents = document.querySelectorAll('.has-dropdown');

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', !isExpanded);
      mainNav.classList.toggle('is-active', !isExpanded);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mainNav.classList.contains('is-active')) {
        mainNav.classList.remove('is-active');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
  }

  // Mobile / keyboard handling for dropdown menus
  dropdownParents.forEach(item => {
    const link = item.querySelector('.nav-link');
    if (link) {
      link.addEventListener('click', (e) => {
        // On touch screens or small viewport, toggle dropdown
        if (window.innerWidth < 992) {
          e.preventDefault();
          const isOpen = item.classList.contains('is-open');
          // Close other open dropdowns
          dropdownParents.forEach(other => {
            if (other !== item) other.classList.remove('is-open');
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
  const sliderTrack = document.querySelector('.slider-track');
  const slides = document.querySelectorAll('.slider-slide');
  const bgItems = document.querySelectorAll('.hero-bg-item');
  const prevBtn = document.querySelector('.slider-prev');
  const nextBtn = document.querySelector('.slider-next');
  const dotsContainer = document.querySelector('.slider-dots');

  if (slides.length > 1) {
    let currentSlide = 0;
    const totalSlides = slides.length;
    let autoplayTimer = null;
    let isPaused = false;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Create pagination dots
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
        dot.classList.toggle('is-active', idx === currentSlide);
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

    // Autoplay logic (4000ms autoplay interval per original specification)
    const startAutoplay = () => {
      if (prefersReducedMotion) return;
      stopAutoplay();
      autoplayTimer = setInterval(() => {
        if (!isPaused) {
          nextSlide();
        }
      }, 4000);
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
    const sliderSection = document.querySelector('.hero-slider-section');
    if (sliderSection) {
      sliderSection.addEventListener('mouseenter', () => { isPaused = true; });
      sliderSection.addEventListener('mouseleave', () => { isPaused = false; });
      sliderSection.addEventListener('focusin', () => { isPaused = true; });
      sliderSection.addEventListener('focusout', () => { isPaused = false; });
      sliderSection.addEventListener('touchstart', () => { isPaused = true; }, { passive: true });
      sliderSection.addEventListener('touchend', () => { isPaused = false; }, { passive: true });
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
          message
        };

        const response = await fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (response.ok) {
          showStatus('success', 'Thank you! Your consultation request has been sent successfully.');
          consultationForm.reset();
        } else {
          showStatus('error', 'There was an issue submitting your request. Please try again or reach out directly via email.');
        }
      } catch (err) {
        showStatus('error', 'Network error encountered while sending request. Please contact us via email.');
      } finally {
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
