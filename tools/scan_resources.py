import re
import sys
from html.parser import HTMLParser

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

class ResourceScanner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.scripts = []
        self.styles = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'link':
            self.links.append(attr_dict)
        elif tag == 'script':
            self.scripts.append(attr_dict)
        elif tag == 'style':
            self.styles.append(attr_dict)

scanner = ResourceScanner()
scanner.feed(html)

with open('tools/resource_inventory.txt', 'w', encoding='utf-8') as out:
    out.write("=== LINK TAGS ===\n")
    for l in scanner.links:
        out.write(f"rel={l.get('rel')} href={l.get('href')} id={l.get('id')}\n")

    out.write("\n=== SCRIPT TAGS ===\n")
    for s in scanner.scripts:
        out.write(f"src={s.get('src')} id={s.get('id')}\n")

print(f"Scanned {len(scanner.links)} links, {len(scanner.scripts)} scripts.")
