import re
from html.parser import HTMLParser

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's find swiper slide elements
# In Elementor, slides often have class "swiper-slide" or "elementor-repeater-item-..."
# Let's locate the swiper container
slider_match = re.search(r'<div class="[^"]*elementor-widget-slides[^"]*".*?<!-- (?:end |\.elementor-widget-slides|div)', html, re.DOTALL)
if slider_match:
    slider_html = slider_match.group(0)
    print("Found slides widget!")
else:
    # let's find all swiper-slide occurrences
    slide_matches = re.finditer(r'<div class="([^"]*swiper-slide[^"]*)"', html)
    for i, m in enumerate(slide_matches):
        print(f"Slide tag {i+1}: class='{m.group(1)}'")

# Let's extract text inside each swiper slide
# Let's write a small parser to extract each slide's content
class SlideExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = []
        self.current_slide = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        if 'swiper-slide' in classes:
            self.current_slide = {
                'classes': attr_dict.get('class', ''),
                'is_duplicate': 'swiper-slide-duplicate' in classes,
                'data_swiper_slide_index': attr_dict.get('data-swiper-slide-index'),
                'texts': []
            }
            self.depth = 1
        elif self.current_slide is not None:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.current_slide is not None:
            self.depth -= 1
            if self.depth <= 0:
                self.slides.append(self.current_slide)
                self.current_slide = None

    def handle_data(self, data):
        if self.current_slide is not None:
            text = data.strip()
            if text:
                self.current_slide['texts'].append(text)

extractor = SlideExtractor()
extractor.feed(html)

print(f"Total extracted slides: {len(extractor.slides)}")
for i, s in enumerate(extractor.slides):
    print(f"Slide #{i+1}: is_dup={s['is_duplicate']}, idx={s['data_swiper_slide_index']}, classes='{s['classes']}'")
    print(f"   Texts: {s['texts']}")
