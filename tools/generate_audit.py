import re
import os
from html.parser import HTMLParser
from collections import defaultdict

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's collect everything
class ComprehensiveAuditor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.stylesheets = []
        self.scripts = []
        self.forms = []
        self.form_fields = []
        self.meaningful_attrs = []
        self.visible_strings = []
        self.ignore_tags = {'script', 'style', 'noscript', 'template'}
        self.ignore_depth = 0
        self.dup_slide_depth = 0
        self.country_depth = 0
        self.current_tag = None
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()

        if tag.lower() in self.ignore_tags:
            self.ignore_depth += 1

        if any('swiper-slide-duplicate' in c for c in classes):
            self.dup_slide_depth += 1
        elif self.dup_slide_depth > 0:
            self.dup_slide_depth += 1

        if any('iti__country-list' in c or 'country-list' in c for c in classes):
            self.country_depth += 1
        elif self.country_depth > 0:
            self.country_depth += 1

        if tag == 'link':
            self.stylesheets.append(attr_dict)
        elif tag == 'script':
            self.scripts.append(attr_dict)
        elif tag == 'a':
            self.links.append(attr_dict)
        elif tag == 'img':
            self.images.append(attr_dict)
        elif tag == 'form':
            self.forms.append(attr_dict)
        elif tag in ('input', 'textarea', 'select', 'button'):
            self.form_fields.append((tag, attr_dict))

        # Check meaningful attributes
        for k, v in attr_dict.items():
            if k in ('alt', 'title', 'placeholder', 'aria-label', 'aria-describedby', 'role') or k.startswith('aria-') or k.startswith('data-'):
                if self.dup_slide_depth == 0 and self.country_depth == 0:
                    self.meaningful_attrs.append((tag, k, v))

    def handle_endtag(self, tag):
        if tag.lower() in self.ignore_tags and self.ignore_depth > 0:
            self.ignore_depth -= 1
        if self.dup_slide_depth > 0:
            self.dup_slide_depth -= 1
        if self.country_depth > 0:
            self.country_depth -= 1

    def handle_data(self, data):
        if self.ignore_depth > 0 or self.dup_slide_depth > 0 or self.country_depth > 0:
            return
        cleaned = ' '.join(data.split())
        if cleaned:
            self.visible_strings.append(cleaned)

auditor = ComprehensiveAuditor()
auditor.feed(html)

# Now let's group all external URLs
all_urls = set(re.findall(r'https?://[^\s"\'<>]+', html))
url_categories = {
    'WordPress Endpoints & Feeds (Dead)': [],
    'Elementor & Plugin Stylesheets (Dead)': [],
    'Elementor & Plugin Scripts (Dead)': [],
    'Theme Assets (Dead)': [],
    'Uploaded Media & Favicons': [],
    'Internal Site Pages (Preserved Target URLs)': [],
    'Google Fonts': [],
    'External Social & Service Links': [],
    'WordPress.org & XMLRPC Standards': []
}

for u in sorted(all_urls):
    if 'fonts.googleapis.com' in u or 'fonts.gstatic.com' in u:
        url_categories['Google Fonts'].append(u)
    elif 'linkedin.com' in u or 'facebook.com' in u or 'twitter.com' in u:
        url_categories['External Social & Service Links'].append(u)
    elif 'gmpg.org' in u or 'w.org' in u or 'wordpress.org' in u:
        url_categories['WordPress.org & XMLRPC Standards'].append(u)
    elif 'wp-content/uploads/2021/07' in u:
        url_categories['Uploaded Media & Favicons'].append(u)
    elif 'wp-content/uploads/elementor/css' in u:
        url_categories['Elementor & Plugin Stylesheets (Dead)'].append(u)
    elif 'wp-content/plugins' in u:
        if u.endswith('.css') or '.css?' in u:
            url_categories['Elementor & Plugin Stylesheets (Dead)'].append(u)
        else:
            url_categories['Elementor & Plugin Scripts (Dead)'].append(u)
    elif 'wp-includes' in u or 'wp-content/themes' in u:
        if u.endswith('.css') or '.css?' in u:
            url_categories['Theme Assets (Dead)'].append(u)
        else:
            url_categories['Elementor & Plugin Scripts (Dead)'].append(u)
    elif 'wp-json' in u or 'xmlrpc.php' in u or '/feed' in u or '/comments/feed' in u:
        url_categories['WordPress Endpoints & Feeds (Dead)'].append(u)
    elif 'hirehrconsultancy.com' in u:
        url_categories['Internal Site Pages (Preserved Target URLs)'].append(u)

# Write docs/AUDIT.md
os.makedirs('docs', exist_ok=True)
with open('docs/AUDIT.md', 'w', encoding='utf-8') as f:
    f.write("# Comprehensive Audit of HireHR Snapshot (`index.html`)\n\n")
    f.write("Generated per Phase 1 requirements of `prompt.txt`.\n\n")
    
    f.write("## 1. Inventory of Visible Text Strings\n\n")
    f.write("Below is every unique visible text string extracted from the document in reading order (ignoring scripts, styles, Swiper loop duplicate slides, and the 245-entry intl phone country list):\n\n")
    seen_texts = set()
    for idx, s in enumerate(auditor.visible_strings, 1):
        if s not in seen_texts:
            seen_texts.add(s)
            f.write(f"- `{s}`\n")
    
    f.write(f"\n*Total unique visible text strings: {len(seen_texts)}*\n\n")
    
    f.write("## 2. Inventory of Links (`<a>`)\n\n")
    f.write("| # | Text / Context | Target `href` | Classes / Attributes |\n")
    f.write("|---|---|---|---|\n")
    for i, a in enumerate(auditor.links, 1):
        href = a.get('href', '(none)')
        cls = a.get('class', '')
        rel = a.get('rel', '')
        f.write(f"| {i} | `{href}` | `{cls}` | `rel={rel}` |\n")

    f.write("\n## 3. Inventory of Images (`<img>`)\n\n")
    for i, img in enumerate(auditor.images, 1):
        f.write(f"### Image {i}\n")
        f.write(f"- **src**: `{img.get('src')}`\n")
        f.write(f"- **alt**: `\"{img.get('alt')}\"` (empty in original)\n")
        f.write(f"- **width / height**: `{img.get('width')}` x `{img.get('height')}`\n")
        f.write(f"- **class**: `{img.get('class')}`\n")
        f.write(f"- **srcset**: `{img.get('srcset')}`\n\n")

    f.write("## 4. Inventory of Form Fields (WPForms #308)\n\n")
    f.write("| Tag | ID | Name | Type | Placeholder | Required | Additional Attributes |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for tag, attrs in auditor.form_fields:
        fid = attrs.get('id', '')
        fname = attrs.get('name', '')
        ftype = attrs.get('type', '')
        fph = attrs.get('placeholder', '')
        freq = 'Yes' if 'required' in attrs else 'No'
        extras = ", ".join(f"{k}='{v}'" for k, v in attrs.items() if k not in ('id', 'name', 'type', 'placeholder', 'required', 'class'))
        f.write(f"| `{tag}` | `{fid}` | `{fname}` | `{ftype}` | `{fph}` | {freq} | `{extras}` |\n")

    f.write("\n## 5. Meaning-Carrying Attributes\n\n")
    f.write("Sample of meaningful attributes (`aria-*`, `role`, `title`, `placeholder`, `data-*`):\n\n")
    for tag, k, v in auditor.meaningful_attrs[:50]:
        f.write(f"- `<{tag}>` `{k}=\"{v}\"`\n")

    f.write("\n## 6. External URLs Referenced by Category\n\n")
    for cat_name, urls in url_categories.items():
        f.write(f"### {cat_name} ({len(urls)} items)\n\n")
        for u in urls:
            f.write(f"- `{u}`\n")
        f.write("\n")

    f.write("## 7. Status Classification: Missing vs. Merely Dead vs. Recovered\n\n")
    f.write("### Recovered Assets\n")
    f.write("- `assets/cropped-Capture-32x32.png`: Successfully retrieved from Internet Archive Wayback Machine snapshot (`20220523025133`).\n\n")
    
    f.write("### Missing Assets & Resources (Permanently Unrecoverable without owner assets)\n")
    f.write("- **Logo (`Logo-Edited-1.png`)**: Not archived on Wayback Machine; DNS for domain fails. Per specification, will render text wordmark `'HireHR consultancy services'`.\n")
    f.write("- **Consultant Image (`Image-Consultant-Course-1024x682.jpg`)**: Not archived on Wayback Machine; DNS for domain fails. Per specification, no stock or AI image substituted.\n")
    f.write("- **Favicons (`cropped-Capture-192x192.png`, `-180x180.png`, `-270x270.png`)**: Not archived on Wayback Machine. The 32x32 version is recovered and will be used.\n")
    f.write("- **Elementor Post Styles (`post-8.css`, `global.css`, `post-141.css`, `post-142.css`)**: Not archived on Wayback Machine. Hero slide backgrounds and layout will use clean modern CSS matching the captured markup with `#cd2653` accent gradient.\n")
    f.write("- **Inner Pages Content (`/about-us/`, etc.)**: Real content was not included in repo snapshot. Inner pages will be created with shared header/footer, page heading, and neutral `data-placeholder=\"content-pending\"` marker.\n\n")
    
    f.write("### Merely Dead Endpoints (Inactive WordPress infrastructure)\n")
    f.write("- `https://hirehrconsultancy.com/xmlrpc.php`: Dead XML-RPC endpoint. Disabled with comment.\n")
    f.write("- `https://hirehrconsultancy.com/wp-json/*`: Dead REST API endpoints. Disabled with comment.\n")
    f.write("- `https://hirehrconsultancy.com/feed/`, `/comments/feed/`: Dead RSS feeds. Disabled with comment.\n")
    f.write("- `wpforms` POST action: Dead endpoint. Disabled in comment; form handled with configurable JS endpoint.\n")
    f.write("- Facebook and Twitter links: Have empty `href=\"\"` in original. Kept inert with `aria-disabled=\"true\"`.\n")

print("Generated docs/AUDIT.md successfully.")
