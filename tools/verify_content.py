import os
import sys
import re
import html
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.extract_text import extract_text

def normalize_text(text):
    if not text:
        return ''
    # Unescape HTML entities
    text = html.unescape(text)
    # Treat ’ (\u2019) and ` as '
    text = text.replace('\u2019', "'").replace('`', "'")
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_refined_copy(copy_path):
    with open(copy_path, 'r', encoding='utf-8') as f:
        content = f.read()

    items = {}

    # home.card.it
    m = re.search(r'`home\.card\.it`[^\n]*\n([^\n]+)', content)
    if m:
        items['home.card.it'] = ('index.html', m.group(1).strip())

    # home.card.ites
    m = re.search(r'`home\.card\.ites`[^\n]*\n([^\n]+)', content)
    if m:
        items['home.card.ites'] = ('index.html', m.group(1).strip())

    # home.card.nonit
    m = re.search(r'`home\.card\.nonit`[^\n]*\n([^\n]+)', content)
    if m:
        items['home.card.nonit'] = ('index.html', m.group(1).strip())

    # home.who
    m = re.search(r'`home\.who`[^\n]*\n([^\n]+)', content)
    if m:
        items['home.who'] = ('index.html', m.group(1).strip())

    # home.why.*
    for why_key in ['experience', 'time', 'tools', 'database', 'cost', 'coordination']:
        pattern = rf'`home\.why\.{why_key}`:\s*([^\n]+)'
        m = re.search(pattern, content)
        if m:
            items[f'home.why.{why_key}'] = ('index.html', m.group(1).strip())

    # about.p1, p2, p3
    m_p1 = re.search(r'-\s*\*\*`about-us/`\*\*.*?-\s*p1:\s*([^\n]+)', content, re.DOTALL)
    m_p2 = re.search(r'-\s*\*\*`about-us/`\*\*.*?-\s*p2:\s*([^\n]+)', content, re.DOTALL)
    m_p3 = re.search(r'-\s*\*\*`about-us/`\*\*.*?-\s*p3:\s*([^\n]+)', content, re.DOTALL)
    if m_p1: items['about.p1'] = ('about-us/index.html', m_p1.group(1).strip())
    if m_p2: items['about.p2'] = ('about-us/index.html', m_p2.group(1).strip())
    if m_p3: items['about.p3'] = ('about-us/index.html', m_p3.group(1).strip())

    # permanent.p1, p2
    m_perm = re.search(r'-\s*\*\*`permanent-hiring-solutions/`\*\*.*?-\s*p1:\s*([^\n]+).*?-\s*p2:\s*([^\n]+)', content, re.DOTALL)
    if m_perm:
        items['permanent.p1'] = ('permanent-hiring-solutions/index.html', m_perm.group(1).strip())
        items['permanent.p2'] = ('permanent-hiring-solutions/index.html', m_perm.group(2).strip())

    # contract.p1, p2
    m_cont = re.search(r'-\s*\*\*`contract-hiring-solutions/`\*\*.*?-\s*p1:\s*([^\n]+).*?-\s*p2:\s*([^\n]+)', content, re.DOTALL)
    if m_cont:
        items['contract.p1'] = ('contract-hiring-solutions/index.html', m_cont.group(1).strip())
        items['contract.p2'] = ('contract-hiring-solutions/index.html', m_cont.group(2).strip())

    # contract_to_hire.p1
    m_c2h = re.search(r'-\s*\*\*`contract-to-hire-solutions/`\*\*.*?-\s*p1:\s*([^\n]+)', content, re.DOTALL)
    if m_c2h:
        items['contract_to_hire.p1'] = ('contract-to-hire-solutions/index.html', m_c2h.group(1).strip())

    # rpo.p1, p2
    m_rpo = re.search(r'-\s*\*\*`recruitment-process-outsourcing/`\*\*.*?-\s*p1:\s*([^\n]+).*?-\s*p2:\s*([^\n]+)', content, re.DOTALL)
    if m_rpo:
        items['rpo.p1'] = ('recruitment-process-outsourcing/index.html', m_rpo.group(1).strip())
        items['rpo.p2'] = ('recruitment-process-outsourcing/index.html', m_rpo.group(2).strip())

    # bgv.h2, p1
    m_bgv_h2 = re.search(r'-\s*\*\*`background-verification-service/`\*\*.*?-\s*h2:\s*([^\n]+)', content, re.DOTALL)
    m_bgv_p1 = re.search(r'-\s*\*\*`background-verification-service/`\*\*.*?-\s*p1:\s*([^\n]+)', content, re.DOTALL)
    if m_bgv_h2: items['bgv.h2'] = ('background-verification-service/index.html', m_bgv_h2.group(1).strip())
    if m_bgv_p1: items['bgv.p1'] = ('background-verification-service/index.html', m_bgv_p1.group(1).strip())

    # our-specialty: 3 h2s and 3 paragraphs (identical to home cards)
    items['specialty.it.h2'] = ('our-specialty/index.html', 'IT Hiring Service')
    items['specialty.it.p'] = ('our-specialty/index.html', items['home.card.it'][1])
    items['specialty.ites.h2'] = ('our-specialty/index.html', 'ITES Hiring Service')
    items['specialty.ites.p'] = ('our-specialty/index.html', items['home.card.ites'][1])
    items['specialty.nonit.h2'] = ('our-specialty/index.html', 'Non-IT Hiring Service')
    items['specialty.nonit.p'] = ('our-specialty/index.html', items['home.card.nonit'][1])

    # career_advice.p1
    m_ca = re.search(r'-\s*\*\*`career-advice/`\*\*.*?-\s*p1:\s*([^\n]+)', content, re.DOTALL)
    if m_ca:
        items['career_advice.p1'] = ('career-advice/index.html', m_ca.group(1).strip())

    # job_seekers
    m_js_h2_1 = re.search(r'-\s*\*\*`job-seekers/`\*\*.*?-\s*h2:\s*Interview Grooming', content, re.DOTALL)
    m_js_p_1 = re.search(r'-\s*\*\*`job-seekers/`\*\*.*?Interview Grooming.*?-\s*p:\s*([^\n]+)', content, re.DOTALL)
    m_js_h2_2 = re.search(r'-\s*\*\*`job-seekers/`\*\*.*?-\s*h2:\s*Resume Guidelines', content, re.DOTALL)
    m_js_p_2 = re.search(r'-\s*\*\*`job-seekers/`\*\*.*?Resume Guidelines.*?-\s*p:\s*([^\n]+)', content, re.DOTALL)
    if m_js_h2_1: items['job_seekers.interview.h2'] = ('job-seekers/index.html', 'Interview Grooming')
    if m_js_p_1: items['job_seekers.interview.p'] = ('job-seekers/index.html', m_js_p_1.group(1).strip())
    if m_js_h2_2: items['job_seekers.resume.h2'] = ('job-seekers/index.html', 'Resume Guidelines')
    if m_js_p_2: items['job_seekers.resume.p'] = ('job-seekers/index.html', m_js_p_2.group(1).strip())

    return items

def run_content_verification():
    report = []
    report.append("# Content Verification Report (`docs/VERIFY_CONTENT.md`)")
    report.append("Executed according to Phase: VERIFICATION (must pass) in `prompt.txt`.\n")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    copy_path = os.path.join(base_dir, 'content', 'refined-copy.md')

    items = parse_refined_copy(copy_path)
    report.append(f"## 1. Refined Copy Verbatim Assertions ({len(items)} items checked)\n")

    all_passed = True
    page_texts_map = {}

    for item_id, (page_rel, expected_text) in sorted(items.items()):
        page_abs = os.path.join(base_dir, page_rel)
        if page_rel not in page_texts_map:
            page_texts_map[page_rel] = [normalize_text(t) for t in extract_text(page_abs)]

        norm_expected = normalize_text(expected_text)

        cnt = page_texts_map[page_rel].count(norm_expected)
        if cnt == 1:
            report.append(f"- [PASS] `{item_id}` on `{page_rel}`: appears exactly once, verbatim.")
        else:
            all_passed = False
            report.append(f"- [FAIL] `{item_id}` on `{page_rel}`: expected exactly 1 occurrence, found {cnt}!")
            report.append(f"  Target: \"{norm_expected[:80]}...\"")

    report.append("")

    # 2. Assert no forbidden strings
    report.append("## 2. Forbidden Words and Character Assertions\n")

    # Site pages excluding original/, docs/, tools/, content/
    site_pages = glob.glob(os.path.join(base_dir, '*.html')) + glob.glob(os.path.join(base_dir, '*', '*.html'))
    site_pages = [p for p in site_pages if not any(x in p.replace('\\', '/') for x in ['/original/', '/docs/', '/tools/', '/content/'])]

    # a) No 'consultancy' in site copy (outside preserved LinkedIn URL)
    consultancy_fails = []
    # b) No em dash
    em_dash_fails = []
    # c) No 'emloyer'
    emloyer_fails = []
    # d) No data-placeholder on any site page
    placeholder_fails = []

    for p in sorted(site_pages):
        rel = os.path.relpath(p, base_dir).replace('\\', '/')
        with open(p, 'r', encoding='utf-8') as f:
            raw = f.read()

        # Check consultancy in copy (ignoring LinkedIn profile URL which retains client's official handle)
        no_linkedin = re.sub(r'https?://[^\s"\']*linkedin\.com[^\s"\']*', '', raw)
        if 'consultancy' in no_linkedin.lower():
            consultancy_fails.append(rel)

        # Em dash check
        if '\u2014' in raw or '&mdash;' in raw or '&#8212;' in raw:
            em_dash_fails.append(rel)

        # emloyer typo check
        if 'emloyer' in raw.lower():
            emloyer_fails.append(rel)

        # data-placeholder check: no site page should have data-placeholder
        has_placeholder = 'data-placeholder' in raw
        if has_placeholder:
            placeholder_fails.append(f"{rel} has unexpected data-placeholder")

    if not consultancy_fails:
        report.append("- [PASS] **No `consultancy` (case-insensitive)** found in site copy on any site page.")
    else:
        all_passed = False
        report.append(f"- [FAIL] `consultancy` found in site copy on: {consultancy_fails}")

    if not em_dash_fails:
        report.append("- [PASS] **No em dash (`—` / `&mdash;`)** found on any site page.")
    else:
        all_passed = False
        report.append(f"- [FAIL] em dash found on: {em_dash_fails}")

    if not emloyer_fails:
        report.append("- [PASS] **No `emloyer` typo** found on any site page.")
    else:
        all_passed = False
        report.append(f"- [FAIL] `emloyer` found on: {emloyer_fails}")

    if not placeholder_fails:
        report.append("- [PASS] **No `data-placeholder` found on any site page (all pages complete)**.")
    else:
        all_passed = False
        report.append(f"- [FAIL] `data-placeholder` check failed: {placeholder_fails}")

    report.append("")

    if all_passed:
        report.append("### RESULT: ALL CONTENT VERIFICATION CHECKS PASSED (100%)\n")
    else:
        report.append("### RESULT: VERIFICATION FAILED\n")

    output_str = '\n'.join(report)
    print(output_str)

    return all_passed, output_str

if __name__ == '__main__':
    success, _ = run_content_verification()
    sys.exit(0 if success else 1)
