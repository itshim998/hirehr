import re
from html.parser import HTMLParser

class OriginalAnalyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.images = []
        self.stylesheets = []
        self.scripts = []
        self.forms = []
        self.inputs = []
        self.meta = []
        self.current_tag = None
        self.text_nodes = []
        self.in_script_or_style = False
        self.in_country_list = False
        self.in_duplicate_slide = False
        self.comments = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.current_tag = tag

        if tag in ('script', 'style'):
            self.in_script_or_style = True

        if tag == 'link':
            rel = attr_dict.get('rel', '')
            href = attr_dict.get('href', '')
            self.stylesheets.append({'rel': rel, 'href': href, 'attrs': attr_dict})

        elif tag == 'script':
            src = attr_dict.get('src', '')
            if src:
                self.scripts.append({'src': src, 'attrs': attr_dict})

        elif tag == 'a':
            self.links.append({'href': attr_dict.get('href', ''), 'attrs': attr_dict})

        elif tag == 'img':
            self.images.append({
                'src': attr_dict.get('src', ''),
                'alt': attr_dict.get('alt', ''),
                'srcset': attr_dict.get('srcset', ''),
                'attrs': attr_dict
            })

        elif tag == 'form':
            self.forms.append(attr_dict)

        elif tag in ('input', 'textarea', 'select', 'button'):
            self.inputs.append({'tag': tag, 'attrs': attr_dict})

        elif tag == 'meta':
            self.meta.append(attr_dict)

        # check for swiper duplicate slide
        classes = attr_dict.get('class', '').split()
        if 'swiper-slide-duplicate' in classes:
            self.in_duplicate_slide = True

        if 'intl-tel-input' in attr_dict.get('class', '') or 'country-list' in attr_dict.get('class', ''):
            self.in_country_list = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.in_script_or_style = False
        if tag == 'div' and self.in_duplicate_slide:
            # Note: could be nested, but swiper slides are divs
            pass

    def handle_comment(self, data):
        self.comments.append(data.strip())

def run():
    with open('original/index.original.html', 'r', encoding='utf-8') as f:
        html = f.read()

    analyzer = OriginalAnalyzer()
    analyzer.feed(html)

    print(f"Total links (<a>): {len(analyzer.links)}")
    print(f"Total images (<img>): {len(analyzer.images)}")
    print(f"Total stylesheets (<link>): {len(analyzer.stylesheets)}")
    print(f"Total scripts (<script src>): {len(analyzer.scripts)}")
    print(f"Total forms: {len(analyzer.forms)}")
    print(f"Total input/textarea/select/button: {len(analyzer.inputs)}")
    print(f"Total meta tags: {len(analyzer.meta)}")

if __name__ == '__main__':
    run()
