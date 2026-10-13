import re
import sys
import json
from html.parser import HTMLParser

class VisibleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.ignore_tags = {'script', 'style', 'noscript', 'template'}
        self.tag_stack = []
        # suppression tracking
        self.ignore_depth = 0
        self.duplicate_slide_depth = 0
        self.country_list_depth = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()

        self.tag_stack.append((tag, attr_dict))

        if tag.lower() in self.ignore_tags:
            self.ignore_depth += 1

        if any('swiper-slide-duplicate' in c for c in classes):
            self.duplicate_slide_depth += 1
        elif self.duplicate_slide_depth > 0:
            self.duplicate_slide_depth += 1

        if any('iti__country-list' in c or 'country-list' in c for c in classes):
            self.country_list_depth += 1
        elif self.country_list_depth > 0:
            self.country_list_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.ignore_tags and self.ignore_depth > 0:
            self.ignore_depth -= 1

        if self.duplicate_slide_depth > 0:
            self.duplicate_slide_depth -= 1

        if self.country_list_depth > 0:
            self.country_list_depth -= 1

        if self.tag_stack:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.ignore_depth > 0:
            return
        if self.duplicate_slide_depth > 0:
            return
        if self.country_list_depth > 0:
            return

        cleaned = ' '.join(data.split())
        if cleaned:
            self.texts.append(cleaned)

def extract_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    extractor = VisibleTextExtractor()
    extractor.feed(content)
    return extractor.texts

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <html_file> [--json] [--unique]")
        sys.exit(1)

    file_path = sys.argv[1]
    texts = extract_text(file_path)

    if '--unique' in sys.argv:
        seen = set()
        unique_texts = []
        for t in texts:
            if t not in seen:
                seen.add(t)
                unique_texts.append(t)
        texts = unique_texts

    if '--json' in sys.argv:
        print(json.dumps(texts, indent=2, ensure_ascii=False))
    else:
        for t in texts:
            print(t)
