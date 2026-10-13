import re

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

country_items = re.findall(r'<li class="iti__country[^"]*".*?</li>', html, re.DOTALL)
print(f"Total iti__country items: {len(country_items)}")
for c in country_items[:5]:
    name = re.search(r'<span class="iti__country-name">(.*?)</span>', c)
    dial = re.search(r'<span class="iti__dial-code">(.*?)</span>', c)
    print(name.group(1) if name else '?', dial.group(1) if dial else '?')
