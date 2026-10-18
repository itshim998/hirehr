# HireHR Services Design System: Quiet Authority

**Version:** 1.0.0 (Foundation)  
**Aesthetic Vision:** Quiet Authority (Boutique Professional-Services Advisory Firm)  
**Status:** Active Foundation (Task 1)  

---

## 1. Overview & Principles

The "Quiet Authority" design system replaces generic SaaS templates (rounded white cards, drop shadows, crimson WordPress defaults, system font stacks) with the understated elegance of an established management advisory firm.

### Core Tenets
1. **Substance over Decoration:** Content structure is communicated through typography, whitespace, subtle hairlines (`1px var(--line)`), and deliberate colour fields—not floating cards or heavy shadows.
2. **Typography First:** High-contrast editorial serif headings (**Newsreader**) paired with precise, readable sans-serif body and UI elements (**Hanken Grotesk**).
3. **Restrained Palette:** Deep inky blues, warm architectural paper tones, and focused teal accents. Crimson `#cd2653` and tinted card backgrounds are strictly eliminated.
4. **Calm, High-Performance Motion:** Micro-interactions and reveals use a single curated easing curve (`cubic-bezier(0.2, 0.7, 0.2, 1)`) animating only `opacity` and `transform`.
5. **Universal Accessibility:** 100% self-hosted zero-cost assets, full keyboard accessibility, zero layout shifts, and all colour pairings strictly verified for WCAG AA compliance (>= 4.5:1 for normal text).

---

## 2. Design Tokens

### 2.1 Color Tokens
All colours are defined as CSS Custom Properties on `:root`:

```css
:root {
  /* Surfaces & Backgrounds */
  --ink: #0A1624;             /* Deep primary dark surface */
  --ink-2: #102235;           /* Secondary dark surface */
  --paper: #F6F4EF;           /* Warm architectural light page background */
  --white: #FFFFFF;           /* Crisp clean card/panel background */

  /* Typography */
  --text: #1B2733;            /* High-contrast body text */
  --muted: #5B6773;           /* Secondary/caption/meta text */

  /* Architectural Lines */
  --line: #D9D5CC;            /* Subtle hairline on light surfaces */
  --line-dark: rgba(255, 255, 255, 0.14); /* Hairline on dark surfaces */

  /* Accents */
  --accent: #22D3CF;          /* Vibrant cyan-teal (on dark surfaces only) */
  --accent-ink: #0A6B6F;      /* Deep rich teal (text/links/buttons on light surfaces) */
  --accent-ink-hover: #085458;/* Hover state for accent-ink */

  /* Functional Status */
  --danger: #B3261E;          /* Error / required fields on light surfaces */
  --danger-on-dark: #FF8A80;  /* Error text on dark surfaces */
}
```

### 2.2 WCAG AA Contrast Verification
Every color pair used across the site has been tested and verified to meet or exceed WCAG AA standards (minimum 4.5:1 for body text, 3.0:1 for large text):

| Foreground | Background | Usage Context | Contrast Ratio | WCAG AA Status |
|:---|:---|:---|:---:|:---:|
| `--text` (`#1B2733`) | `--paper` (`#F6F4EF`) | Main body copy on page | **13.80:1** | PASS (AAA) |
| `--text` (`#1B2733`) | `--white` (`#FFFFFF`) | Content text on white | **15.17:1** | PASS (AAA) |
| `--muted` (`#5B6773`) | `--paper` (`#F6F4EF`) | Secondary / caption text | **5.26:1** | PASS (AA) |
| `--muted` (`#5B6773`) | `--white` (`#FFFFFF`) | Secondary text on white | **5.78:1** | PASS (AA) |
| `--accent-ink` (`#0A6B6F`) | `--paper` (`#F6F4EF`) | Text links & buttons on paper | **5.71:1** | PASS (AA) |
| `--accent-ink` (`#0A6B6F`) | `--white` (`#FFFFFF`) | Text links & buttons on white | **6.28:1** | PASS (AA) |
| `--accent-ink-hover` (`#085458`) | `--paper` (`#F6F4EF`) | Hover states on paper | **7.90:1** | PASS (AAA) |
| `--accent-ink-hover` (`#085458`) | `--white` (`#FFFFFF`) | Hover states on white | **8.68:1** | PASS (AAA) |
| `--accent` (`#22D3CF`) | `--ink` (`#0A1624`) | Eyebrows / links on footer/dark | **9.79:1** | PASS (AAA) |
| `--white` (`#FFFFFF`) | `--ink` (`#0A1624`) | Headings & text on ink | **18.21:1** | PASS (AAA) |
| `--white` (`#FFFFFF`) | `--accent-ink` (`#0A6B6F`) | Primary button text | **6.28:1** | PASS (AA) |
| `--ink` (`#0A1624`) | `--accent` (`#22D3CF`) | Dark button text on teal | **9.79:1** | PASS (AAA) |
| `--danger` (`#B3261E`) | `--white` (`#FFFFFF`) | Form error message | **6.54:1** | PASS (AA) |

---

## 3. Typography

Self-hosted under `assets/fonts/` with SIL Open Font License 1.1 (zero CDN dependencies, zero telemetry, full offline functionality).

- **Headings / Wordmark:** `Newsreader` (Variable font, weights 400–600).
  - Fallback stack: `"Newsreader", "Source Serif 4", Georgia, serif`
- **Body / Interface:** `Hanken Grotesk` (Variable font, weights 400–700).
  - Fallback stack: `"Hanken Grotesk", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif`

### Critical Preloading
Both critical fonts are preloaded in `<head>` on all pages:
```html
<link rel="preload" href="assets/fonts/newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/hanken-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
```

### Type Scale (Fluid)
| Level | Family | Weight | Size / Line-Height | Tracking | Notes |
|:---|:---|:---:|:---|:---:|:---|
| **Hero H1** | Newsreader | 500 | `clamp(2.75rem, 5.4vw, 4.75rem) / 1.04` | `-0.015em` | Homepage Hero |
| **Editorial H1** | Newsreader | 500 | `clamp(2.5rem, 5.0vw, 4.00rem) / 1.08` | `-0.015em` | Inner pages + 56px rule |
| **H2 Section** | Newsreader | 500 | `clamp(1.9rem, 3.2vw, 2.75rem) / 1.15` | normal | Section headers / inner topics |
| **H3 Subsection** | Newsreader | 500 | `clamp(1.35rem, 1.8vw, 1.65rem) / 1.25` | normal | Card & group titles |
| **Lead Paragraph** | Hanken Grotesk | 400 | `clamp(1.125rem, 1.4vw, 1.3rem) / 1.70` | normal | Subtitles, intro text |
| **Body Copy** | Hanken Grotesk | 400 | `1.0625rem (17px) / 1.70` | normal | Standard reading copy |
| **Editorial Body** | Hanken Grotesk | 400 | `1.125rem (18px) / 1.80` | normal | Inner page reading column |
| **Eyebrow / Badges**| Hanken Grotesk | 600 | `0.8125rem (13px)` | `0.14em` | UPPERCASE section labels |
| **Nav Links** | Hanken Grotesk | 600 | `0.8125rem (13px)` | `0.08em` | UPPERCASE navigation items |

---

## 4. Spacing, Grid & Layout

- **Base Unit:** 8px spacing scale (`--space-1: 8px` through `--space-16: 128px`).
- **Container Max-Width:** `1240px`.
- **Side Padding:**
  - Mobile (<768px): `20px`
  - Tablet (768px–1023px): `32px`
  - Desktop (>=1024px): `40px`
- **Section Padding:** `clamp(72px, 9vw, 128px) 0`
- **Breakpoints:**
  - `480px` (Small mobile)
  - `768px` (Tablet portrait)
  - `1024px` (Desktop / Nav breakpoint)
  - `1280px` (Wide desktop)
- **Radii:** `0px` default for containers/cards. Maximum `2px` for buttons and form inputs (`--radius-btn: 2px`).
- **No Drop Shadows:** `box-shadow` is completely forbidden across the site (`grep -c "box-shadow"` = 0).

---

## 5. Components

### 5.1 Buttons
- **Height & Spacing:** Fixed height `52px`, padding `0 32px`, sans 600, border-radius `2px`, no shadow.
- **Light Surfaces (`.btn-primary`):** Ink fill (`#0A1624`), white text. On hover/focus, an accent wipe (`#0A6B6F`) sweeps smoothly from left to right using a GPU-accelerated `transform: scaleX(1)` transition.
- **Dark Surfaces (`.btn-on-dark`):** Cyan-teal fill (`#22D3CF`), ink text. On hover/focus, white wipe sweeps from left to right.

### 5.2 Text Links
Underlines are drawn dynamically using CSS `background-size` transition (0% to 100%, 350ms ease) upon hover or keyboard `:focus-visible`.

### 5.3 Site Header
- **Top Bar (36px):** Dark ink background (`#0A1624`), hairline bottom (`rgba(255,255,255,.14)`), `0.8125rem` muted text, contact emails and bare LinkedIn icon turning `--accent` on hover. Collapses away smoothly (`margin-top: -36px; opacity: 0; pointer-events: none;`) when the user scrolls past 24px.
- **Main Bar (76px desktop / 64px mobile):**
  - **Homepage:** Transparent over the hero slider at `scrollY < 24px` with white wordmark and white nav links. When scrolled (`.is-scrolled`), transitions to frosted paper (`rgba(246,244,239,.92)`, `backdrop-filter: blur(12px)`), hairline bottom, and ink text.
  - **Inner Pages (`.is-solid`):** Solid paper background from the initial state with a subtle hairline divider.
- **Wordmark:** Unaltered flame logo symbol + "HireHR services" in serif 500 (`1.35rem`).
- **Nav Links:** UPPERCASE sans links with 2px underline sweep. Active page has a permanent 2px underline (no pill badge).
- **Desktop Dropdown:** Clean white panel with `1px var(--line)` border, no shadow, 8px fade/slide-in transition, fully keyboard accessible.
- **Mobile Menu (<1024px):** Toggle opens a full-viewport ink overlay (`#0A1624`) with large serif links (`2rem`), 40ms staggered fade-up, accordion submenus, body scroll lock, and Escape key dismissal with focus returned to the toggle button.

### 5.4 Editorial Inner Pages
- Clear paper background without distracting banners.
- Left-aligned Newsreader `h1` with an architectural `56px x 2px` `--accent-ink` rule.
- Reading column restricted to `max-width: 68ch` for optimal reading comprehension.
- Section `h2` elements in serif with a `1px var(--line)` divider above.
- Contact Us placeholder rendered as subtle italicized muted text without dashed card boxes.

### 5.5 Footer
- Ink background with 3 columns: Brand + Contact, Quick Links (2 columns), and Follow Us.
- Column titles in uppercase eyebrow style in cyan-teal (`--accent`).
- 44px brand logo.
- `1px var(--line-dark)` divider above the centered, muted copyright line.

---

## 6. Motion Infrastructure

Implemented in self-contained `js/ui.js` (< 3 KB) and CSS:

```css
:root {
  --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
  --duration-micro: 180ms;
  --duration-hover: 350ms;
  --duration-reveal: 700ms;
}
```

### 6.1 Reveal-on-Scroll (`[data-reveal]`)
- **Behavior:** Elements marked with `data-reveal` fade in and translate upward by 16px over 700ms using `--ease`.
- **Sibling Stagger:** Sibling reveal elements are staggered by 70ms per index (maximum 5 items via `--reveal-index`).
- **Fail-Safe Robustness:** Elements are hidden **only** if `@media (scripting: enabled)` matches AND `html.has-reveal` has been set by `js/ui.js`. If `ui.js` is blocked, fails to load, or `IntersectionObserver` is unavailable, all content remains 100% visible immediately.
- **View Transitions:** Enabled via CSS `@view-transition { navigation: auto; }` for modern browsers.

### 6.2 Reduced Motion Compliance
When `prefers-reduced-motion: reduce` is detected:
- Reveal translations and delays are disabled.
- Link underlines and button wipe animations change instantaneously.
- View transitions duration is zeroed out.

---

## 7. How to Add `data-reveal`

To add reveal animation to any element:
1. Simply add the `data-reveal` attribute to the container in HTML:
   ```html
   <div class="my-section-header" data-reveal>
     <h2>Heading</h2>
     <p>Description</p>
   </div>
   ```
2. For lists of sibling items (e.g. cards, columns):
   ```html
   <div class="item" data-reveal>Item 1</div>
   <div class="item" data-reveal>Item 2</div>
   <div class="item" data-reveal>Item 3</div>
   ```
   `js/ui.js` automatically detects sibling relationships and applies `--reveal-index: 0, 1, 2...` for staggered entrance.

---

## 8. Accessibility (A11y) Notes

- **Keyboard Focus:** High-contrast `2px solid` focus rings with `3px` offset (`--accent-ink` on light, `--accent` on dark).
- **Skip Links:** Skip-to-content links on every page for assistive navigation.
- **ARIA Attributes:** Full support for `aria-expanded`, `aria-controls`, `aria-haspopup`, and `sr-only` screen-reader labels.
- **Scroll Padding:** `scroll-padding-top: 88px` prevents anchor links from being obscured by sticky headers.
