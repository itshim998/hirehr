# HireHR Services - Static Website

A clean, fast, responsive, and accessible static website for **HireHR services** (recruitment firm based in Kolkata, India).

Rebuilt from a WordPress/Elementor snapshot into a clean static website without frameworks, build steps, or external dependencies.

## Key Features

- **Semantic HTML5 & Vanilla CSS/JS**: No frameworks, no build step, no jQuery/WordPress dependencies.
- **Exact Content Fidelity**: 100% of visible copy, structure, links, form fields, and attributes preserved from the original snapshot.
- **Responsive & Mobile-First**: Tested across viewport widths (375px, 768px, 1280px) with custom mobile navigation.
- **Accessible (WCAG AA compliant)**: Skip link, ARIA landmarks and states, explicit form labels, visible focus indicators, and prefers-reduced-motion support.
- **Design System ("Quiet Authority")**: Built with bespoke typography (self-hosted Newsreader & Hanken Grotesk OFL variable fonts), zero container drop shadows, editorial hairlines, and 100% WCAG AA color tokens. See [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) for full design system guidelines.
- **Hero Slider**: Lightweight vanilla JavaScript slider with 4s autoplay, infinite looping, smooth transitions, and interaction pause.
- **International Consultation Form**: WPForms #308 recreated with 5 required fields, 243-country code selector defaulting to United States (+1), client validation, and configurable endpoint.

## Project Structure

```
hirehr/
├── .nojekyll                           # Prevents GitHub Pages Jekyll processing
├── 404.html                            # Custom static 404 error page
├── index.html                          # Main homepage
├── prompt.txt                          # Task specification and requirements
├── README.md                           # Project documentation
├── robots.txt                          # Search engine crawling rules
├── sitemap.xml                         # XML sitemap
│
├── about-us/index.html                 # About Us page
├── background-verification-service/    # Background Verification Service page
├── career-advice/index.html            # Career Advice page
├── contact-us/index.html               # Contact Us page
├── contract-hiring-solutions/          # Contract Hiring Solutions page
├── contract-to-hire-solutions/         # Contract to Hire Solutions page
├── job-seekers/index.html              # Career Assistance page
├── our-specialty/index.html            # Our Speciality page
├── permanent-hiring-solutions/         # Permanent Hiring Solutions page
├── recruitment-process-outsourcing/    # Recruitment Process Outsourcing page
│
├── assets/
│   └── cropped-Capture-32x32.png       # Favicon recovered from Wayback Machine
│
├── css/
│   └── style.css                       # Single consolidated stylesheet
│
├── js/
│   ├── countries.js                    # 243 country dial codes for phone field
│   └── main.js                         # Slider, mobile nav, and form logic
│
├── original/
│   └── index.original.html             # Verified pristine copy of original snapshot
│
├── docs/
│   ├── AUDIT.md                        # Phase 1 comprehensive audit inventory
│   ├── DEPLOY.md                       # Deployment guide for Cloudflare Workers
│   ├── DESIGN_SYSTEM.md                # Quiet Authority design system specifications
│   ├── REPORT.md                       # Comprehensive project status report
│   ├── ROLLBACK.md                     # Production emergency rollback procedure
│   ├── VERIFY.md                       # Phase 4 verification test logs
│   └── VERIFY_DESIGN.md                # Design upgrade verification & final gates
│
└── tools/
    ├── extract_text.py                 # Text extraction verification script
    ├── generate_audit.py               # Audit generation script
    └── build_inner_pages.py            # Inner pages scaffolding script
```

## Running Locally

### Option 1: Cloudflare Wrangler (Recommended - Full Stack)
Runs both the static site and the `/api/contact` backend Worker locally with Turnstile testing keys:
```bash
npx wrangler dev
```
Then visit `http://127.0.0.1:8787` in your web browser. Local secrets and overrides are read automatically from `.dev.vars` (see `.dev.vars.example`).

### Option 2: Python HTTP Server (Static Pages Only)
```bash
python -m http.server 8000
```
Then visit `http://localhost:8000` in your web browser.

### Option 3: Node / npx
```bash
npx serve .
```

## Backend Architecture (Cloudflare Workers + Static Assets)

The site is deployed as a single unified **Cloudflare Workers with Static Assets** deployment:
- **Routing**: Static assets (`index.html`, inner pages, `css/`, `js/`, `assets/`) are served directly at the edge via Cloudflare's global CDN without invoking the Worker. The Worker script only intercepts `/api/*` requests (`run_worker_first: ["/api/*"]`).
- **Endpoint**: `POST /api/contact` accepts JSON submissions from `#consultation-form`.
- **Bot Protection**: Cloudflare Turnstile explicitly rendered above the Submit button with server-side `siteverify` verification.
- **Spam Defense**: Hidden honeypot field (`website`) silently traps automated submissions.
- **Security Headers**: Standard security headers (`X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: DENY`, and strict CSP) configured via `_headers`.
- **Privacy Enforcement**: Non-public code and files (`worker/`, `wrangler.jsonc`, `tools/`, `docs/`, `original/`, `content/`, `.dev.vars`) are excluded from edge asset uploads via `.assetsignore`.

### Environment Variables & Secrets

Configured in `wrangler.jsonc` and Cloudflare Dashboard / Wrangler secrets:

| Name | Type | Description | Default / Example |
| :--- | :--- | :--- | :--- |
| `ALLOWED_ORIGINS` | Var | Comma-separated allowed CORS origins | `http://localhost:8787` |
| `MAIL_MODE` | Var | Email mode: `"log"` (Stage A) or `"send"` (Stage B) | `"log"` |
| `MAIL_FROM` | Var | Sender address on custom domain (Stage B) | `""` (e.g. `employer@hirehrservices.com`) |
| `TURNSTILE_SECRET` | Secret | Cloudflare Turnstile secret key | Documented always-pass test key in dev |
| `NOTIFY_TO` | Secret | Owner destination email (Stage B) | `owner@example.com` |

## Deployment & Verification

For comprehensive deployment instructions for Stage A (*.workers.dev) and Stage B (hirehrservices.com), refer to:
- **Deployment Guide**: [`docs/DEPLOY.md`](docs/DEPLOY.md)
- **Backend Verification**: [`docs/VERIFY_BACKEND.md`](docs/VERIFY_BACKEND.md)
- **Automated Test Suite**:
  ```bash
  python tools/test_backend.py
  ```

