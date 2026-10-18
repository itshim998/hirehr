import os
import sys
import argparse
import subprocess
import html
import re
import difflib
from html.parser import HTMLParser

PAGES = [
    'index.html',
    '404.html',
    'about-us/index.html',
    'permanent-hiring-solutions/index.html',
    'contract-hiring-solutions/index.html',
    'contract-to-hire-solutions/index.html',
    'recruitment-process-outsourcing/index.html',
    'background-verification-service/index.html',
    'our-specialty/index.html',
    'career-advice/index.html',
    'job-seekers/index.html',
    'contact-us/index.html'
]

def normalize_text_token(text):
    if not text:
        return ''
    text = html.unescape(text)
    # normalize curly/straight apostrophes
    text = text.replace('\u2019', "'").replace('\u2018', "'").replace('`', "'").replace('\u02bc', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class TextAndHrefExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.hrefs = set()
        self.ignore_tags = {'script', 'style', 'svg'}
        self.ignore_depth = 0
        self.title = None
        self.meta_description = None
        self._in_title = False
        self._title_chunks = []

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in self.ignore_tags:
            self.ignore_depth += 1
            return

        attr_dict = {k.lower(): v for k, v in attrs}

        if tag_lower == 'title':
            self._in_title = True
            self._title_chunks = []
        elif tag_lower == 'meta':
            name = attr_dict.get('name', '').lower()
            if name == 'description':
                self.meta_description = normalize_text_token(attr_dict.get('content', ''))

        if tag_lower == 'a':
            href = attr_dict.get('href')
            if href is not None:
                self.hrefs.add(href.strip())

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.ignore_tags and self.ignore_depth > 0:
            self.ignore_depth -= 1
            return

        if tag_lower == 'title':
            self._in_title = False
            self.title = normalize_text_token(''.join(self._title_chunks))

    def handle_data(self, data):
        if self.ignore_depth > 0:
            return
        if self._in_title:
            self._title_chunks.append(data)
            return

        cleaned = normalize_text_token(data)
        if cleaned:
            self.texts.append(cleaned)

def extract_page_data(html_content):
    # Remove HTML comments first
    cleaned_html = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    parser = TextAndHrefExtractor()
    parser.feed(cleaned_html)
    return {
        'title': parser.title,
        'meta_description': parser.meta_description,
        'texts': parser.texts,
        'hrefs': parser.hrefs
    }

def get_base_html(base_ref, rel_path, repo_root):
    # git show expects forward slashes
    git_path = rel_path.replace('\\', '/')
    cmd = ['git', 'show', f'{base_ref}:{git_path}']
    res = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    if res.returncode != 0:
        raise RuntimeError(f"Failed to read {git_path} from {base_ref}: {res.stderr}")
    return res.stdout

def get_local_html(rel_path, repo_root):
    full_path = os.path.join(repo_root, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Verify that text content and hrefs have not changed relative to base branch.")
    parser.add_argument('--base', default='origin/main', help="Base git ref to compare against (default: origin/main)")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_passed = True

    print(f"Comparing working tree against base ref '{args.base}'...\n")

    for page in PAGES:
        try:
            base_html = get_base_html(args.base, page, repo_root)
            local_html = get_local_html(page, repo_root)
        except Exception as e:
            print(f"[{page}] ERROR: {e}")
            all_passed = False
            continue

        base_data = extract_page_data(base_html)
        local_data = extract_page_data(local_html)

        page_errors = []

        # Check title
        if base_data['title'] != local_data['title']:
            page_errors.append(f"Title mismatch:\n  Base:  '{base_data['title']}'\n  Local: '{local_data['title']}'")

        # Check meta description
        if base_data['meta_description'] != local_data['meta_description']:
            page_errors.append(f"Meta description mismatch:\n  Base:  '{base_data['meta_description']}'\n  Local: '{local_data['meta_description']}'")

        # Check ordered texts
        if base_data['texts'] != local_data['texts']:
            diff = difflib.unified_diff(
                base_data['texts'],
                local_data['texts'],
                fromfile=f"base ({args.base}):{page}",
                tofile=f"working_tree:{page}",
                lineterm=''
            )
            page_errors.append("Text sequence mismatch:\n" + "\n".join(diff))

        # Check hrefs (all base hrefs must exist in local)
        missing_hrefs = base_data['hrefs'] - local_data['hrefs']
        if missing_hrefs:
            page_errors.append(f"Missing base hrefs: {sorted(missing_hrefs)}")

        if page_errors:
            print(f"FAIL: {page}")
            for err in page_errors:
                print(f"  - {err}")
            all_passed = False
        else:
            print(f"PASS: {page} (texts: {len(local_data['texts'])}, hrefs: {len(local_data['hrefs'])})")

    print("\n" + ("=" * 40))
    if all_passed:
        print("RESULT: ALL PAGES PASSED - NO TEXT OR BASE HREF LOSS DETECTED.")
        sys.exit(0)
    else:
        print("RESULT: VERIFICATION FAILED - CONTENT OR LINK DIFFERENCES FOUND.")
        sys.exit(1)

if __name__ == '__main__':
    main()
