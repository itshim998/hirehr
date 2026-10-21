import os
import json

PAGES_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'content', 'pages.json')
pages_data = {}
if os.path.exists(PAGES_JSON_PATH):
    with open(PAGES_JSON_PATH, 'r', encoding='utf-8') as f:
        pages_data = json.load(f)

inner_pages = [
    {
        'dir': 'about-us',
        'heading': 'ABOUT US',
        'nav_active': 'about-us'
    },
    {
        'dir': 'permanent-hiring-solutions',
        'heading': 'Permanent Hiring',
        'nav_active': 'permanent-hiring-solutions'
    },
    {
        'dir': 'contract-hiring-solutions',
        'heading': 'Contract Hiring',
        'nav_active': 'contract-hiring-solutions'
    },
    {
        'dir': 'contract-to-hire-solutions',
        'heading': 'Contract to Hire',
        'nav_active': 'contract-to-hire-solutions'
    },
    {
        'dir': 'recruitment-process-outsourcing',
        'heading': 'Recruitment Process Outsourcing',
        'nav_active': 'recruitment-process-outsourcing'
    },
    {
        'dir': 'background-verification-service',
        'heading': 'Background Verification Service',
        'nav_active': 'background-verification-service'
    },
    {
        'dir': 'our-specialty',
        'heading': 'Our Speciality',
        'nav_active': 'our-specialty'
    },
    {
        'dir': 'career-advice',
        'heading': 'Career Advice',
        'nav_active': 'career-advice'
    },
    {
        'dir': 'job-seekers',
        'heading': 'Career Assistance',
        'nav_active': 'job-seekers'
    },
    {
        'dir': 'contact-us',
        'heading': 'CONTACT US',
        'nav_active': 'contact-us'
    }
]

def generate_inner_page(page_info):
    target_dir = page_info['dir']
    heading = page_info['heading']
    nav_active = page_info['nav_active']
    
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, 'index.html')

    meta_desc = "HireHR Services is a manpower hiring service provider headquartered in Kolkata, West Bengal."
    if target_dir in pages_data and 'meta_description' in pages_data[target_dir]:
        meta_desc = pages_data[target_dir]['meta_description']

    if target_dir == 'contact-us':
        main_content = """        <div class="pending-card" data-reveal>
          <p data-placeholder="content-pending">Content pending from site owner.</p>
        </div>"""
    elif target_dir in pages_data and 'content_html' in pages_data[target_dir]:
        raw_html = pages_data[target_dir]['content_html']
        indented_html = '\n'.join('          ' + line if line.strip() else '' for line in raw_html.splitlines())
        main_content = f"""        <div class=\"page-body\" data-reveal>
{indented_html}
        </div>"""
    else:
        main_content = """        <div class="pending-card" data-reveal>
          <p data-placeholder="content-pending">Content pending from site owner.</p>
        </div>"""
    
    html = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{heading} - HireHR services</title>
  <link rel="canonical" href="https://hirehrservices.com/{target_dir}/">
  <meta name="robots" content="max-image-preview:large">
  <meta name="theme-color" content="#0A1624">
  <meta name="description" content="{meta_desc}">
  <link rel="preload" href="../assets/fonts/newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/hanken-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/cropped-Capture-32x32.png">
  <link rel="stylesheet" href="../css/style.css">

  <!-- DISABLED (WordPress infrastructure inactive):
  <link rel="profile" href="http://gmpg.org/xfn/11">
  <link rel="pingback" href="https://hirehrservices.com/xmlrpc.php">
  <link rel="alternate" type="application/rss+xml" title="HireHR services &raquo; Feed" href="https://hirehrservices.com/feed/">
  <link rel="alternate" type="application/rss+xml" title="HireHR services &raquo; Comments Feed" href="https://hirehrservices.com/comments/feed/">
  <link rel="https://api.w.org/" href="https://hirehrservices.com/wp-json/">
  <link rel="EditURI" type="application/rsd+xml" title="RSD" href="https://hirehrservices.com/xmlrpc.php?rsd">
  <link rel="shortlink" href="https://hirehrservices.com/{target_dir}/">
  -->
</head>
<body>
  <!-- Skip Link for Accessibility -->
  <a href="#site-content" class="skip-link">Skip to the content</a>

  <!-- Header -->
  <header class="site-header is-solid">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="container">
        <div class="top-bar-emails">
          <a href="mailto:info@hirehrservices.com">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            info@hirehrservices.com
          </a>
        </div>
      </div>
    </div>

    <!-- Main Navigation Bar -->
    <div class="nav-bar">
      <div class="container">
        <!-- Logo Wordmark (Original image unrecoverable) -->
        <!-- DISABLED (image unrecoverable from dead domain/archive): <img src="wp-content/uploads/2021/07/Logo-Edited-1.png" alt="HireHR services" width="389" height="156"> -->
        <a href="../index.html" class="brand-wordmark"><img src="../assets/logo/hirehr-logo.png" srcset="../assets/logo/hirehr-logo.png 1x, ../assets/logo/hirehr-logo-2x.png 2x" alt="" width="22" height="44">HireHR services</a>

        <!-- Mobile Menu Toggle Button -->
        <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="primary-nav">
          <span>Menu</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
        </button>

        <!-- Main Navigation Links -->
        <nav id="primary-nav" class="main-navigation" aria-label="Primary Navigation">
          <ul class="nav-menu">
            <li class="nav-item">
              <a href="../index.html" class="nav-link">HOME</a>
            </li>
            <li class="nav-item">
              <a href="../about-us/index.html" class="nav-link {'active' if nav_active == 'about-us' else ''}">ABOUT US</a>
            </li>
            <li class="nav-item has-dropdown">
              <a href="#" class="nav-link {'active' if nav_active in ['permanent-hiring-solutions', 'contract-hiring-solutions', 'contract-to-hire-solutions', 'recruitment-process-outsourcing', 'background-verification-service', 'our-specialty'] else ''}" aria-haspopup="true" aria-expanded="false">
                EMPLOYERS
                <span class="dropdown-toggle-icon" aria-hidden="true">&#9662;</span>
              </a>
              <ul class="dropdown-menu">
                <li><a href="../permanent-hiring-solutions/index.html" class="dropdown-link {'active' if nav_active == 'permanent-hiring-solutions' else ''}">Permanent Hiring</a></li>
                <li><a href="../contract-hiring-solutions/index.html" class="dropdown-link {'active' if nav_active == 'contract-hiring-solutions' else ''}">Contract Hiring</a></li>
                <li><a href="../contract-to-hire-solutions/index.html" class="dropdown-link {'active' if nav_active == 'contract-to-hire-solutions' else ''}">Contract to Hire</a></li>
                <li><a href="../recruitment-process-outsourcing/index.html" class="dropdown-link {'active' if nav_active == 'recruitment-process-outsourcing' else ''}">Recruitment Process Outsourcing</a></li>
                <li><a href="../background-verification-service/index.html" class="dropdown-link {'active' if nav_active == 'background-verification-service' else ''}">Background Verification Service</a></li>
                <li><a href="../our-specialty/index.html" class="dropdown-link {'active' if nav_active == 'our-specialty' else ''}">Our Speciality</a></li>
              </ul>
            </li>
            <li class="nav-item has-dropdown">
              <a href="#" class="nav-link {'active' if nav_active in ['career-advice', 'job-seekers'] else ''}" aria-haspopup="true" aria-expanded="false">
                JOB SEEKERS
                <span class="dropdown-toggle-icon" aria-hidden="true">&#9662;</span>
              </a>
              <ul class="dropdown-menu">
                <li><a href="../career-advice/index.html" class="dropdown-link {'active' if nav_active == 'career-advice' else ''}">Career Advice</a></li>
                <li><a href="../job-seekers/index.html" class="dropdown-link {'active' if nav_active == 'job-seekers' else ''}">Career Assistance</a></li>
              </ul>
            </li>
            <li class="nav-item">
              <a href="../contact-us/index.html" class="nav-link {'active' if nav_active == 'contact-us' else ''}">CONTACT US</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </header>

  <!-- Main Content Landmark -->
  <main id="site-content">
    <section class="page-hero">
      <div class="container">
        <h1 data-reveal>{heading}</h1>
      </div>
    </section>

    <section class="page-content-section">
      <div class="container">
{main_content}
      </div>
    </section>
  </main>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <!-- Footer Column 1: Contact Info -->
        <div class="footer-col footer-brand" data-reveal>
          <!-- DISABLED (image unrecoverable from dead domain/archive): <img src="wp-content/uploads/2021/07/Logo-Edited-1.png" alt="HireHR services" width="389" height="156"> -->
          <a href="../index.html" class="brand-wordmark" style="color: var(--white); margin-bottom: 1rem;"><img src="../assets/logo/hirehr-logo.png" srcset="../assets/logo/hirehr-logo.png 1x, ../assets/logo/hirehr-logo-2x.png 2x" alt="" width="22" height="44">HireHR services</a>
          <ul class="footer-contact-list">
            <li>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>KL-1 Aswininagar, Baguiati, Kolkata-700159</span>
            </li>
            <li>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <a href="tel:+918296558406">+91 8296558406</a>
            </li>
            <li>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
              <a href="mailto:info@hirehrservices.com">info@hirehrservices.com</a>
            </li>
          </ul>
        </div>

        <!-- Footer Column 2: Quick Links -->
        <div class="footer-col" data-reveal>
          <h2 class="footer-col-title">Quick Links</h2>
          <div class="footer-links-grid">
            <a href="../index.html">Home</a>
            <a href="../about-us/index.html">About Us</a>
            <a href="../permanent-hiring-solutions/index.html">Permanent Hiring Solutions</a>
            <a href="../contract-hiring-solutions/index.html">Contract hiring Solutions</a>
            <a href="../contract-to-hire-solutions/index.html">Contract to Hire Solutions</a>
            <a href="../recruitment-process-outsourcing/index.html">Recruitment Process Outsourcing</a>
            <a href="../background-verification-service/index.html">Background Verification Service</a>
            <a href="../our-specialty/index.html">Our Speciality</a>
            <a href="../career-advice/index.html">Career Advice</a>
            <a href="../job-seekers/index.html">Career Assistance</a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        Copyright &copy; 2021
      </div>
    </div>
  </footer>

  <script src="../js/ui.js" defer></script>
  <script src="../js/main.js"></script>
</body>
</html>
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {file_path}")

for p in inner_pages:
    generate_inner_page(p)

print("All inner pages generated successfully.")
