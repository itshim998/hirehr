# HireHR Consultancy Services - Static Website

A clean, fast, responsive, and accessible static website for **HireHR consultancy services** (recruitment firm based in Kolkata, India).

Rebuilt from a WordPress/Elementor snapshot into a clean static website without frameworks, build steps, or external dependencies.

## Key Features

- **Semantic HTML5 & Vanilla CSS/JS**: No frameworks, no build step, no jQuery/WordPress dependencies.
- **Exact Content Fidelity**: 100% of visible copy, structure, links, form fields, and attributes preserved from the original snapshot.
- **Responsive & Mobile-First**: Tested across viewport widths (375px, 768px, 1280px) with custom mobile navigation.
- **Accessible (WCAG AA compliant)**: Skip link, ARIA landmarks and states, explicit form labels, visible focus indicators, and prefers-reduced-motion support.
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
│   ├── REPORT.md                       # Comprehensive status report
│   └── VERIFY.md                       # Phase 4 verification test logs
│
└── tools/
    ├── extract_text.py                 # Text extraction verification script
    ├── generate_audit.py               # Audit generation script
    └── build_inner_pages.py            # Inner pages scaffolding script
```

## Running Locally

Because the site uses purely relative links and zero external runtime dependencies, it can be previewed using any static file server:

### Option 1: Python HTTP Server (Recommended)
```bash
python -m http.server 8000
```
Then visit `http://localhost:8000` in your web browser.

### Option 2: Node / npx
```bash
npx serve .
```

### Option 3: Direct File Opening
You can open `index.html` directly in any web browser without a web server.

## Deploying to GitHub Pages

1. Push the repository to GitHub:
   ```bash
   git push origin ready-site:main
   ```
2. Navigate to your repository settings: **Settings > Pages**.
3. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: `main` / `ready-site` (root `/`)
4. Save. Your site will be published at `https://<username>.github.io/<repo>/`.

## Deploying to Production Domain (`hirehrconsultancy.com`)

1. Upload all repository files to your web server's web root (`public_html` or equivalent).
2. Configure DNS A / CNAME records to point to your hosting server.
3. If using GitHub Pages with a custom domain, add a `CNAME` file containing `hirehrconsultancy.com` in the root directory.

## Form Submission Configuration

In `js/main.js`, configure the form destination endpoint:

```javascript
// Change null to your designated endpoint URL:
const FORM_ENDPOINT = "https://formspree.io/f/your-form-id"; 
```

When `FORM_ENDPOINT` is `null`, client-side validation still executes, and submitting displays a non-misleading status message indicating that the endpoint is pending configuration.
