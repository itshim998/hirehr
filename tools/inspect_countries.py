import re
from html.parser import HTMLParser

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect country-list
countries = re.findall(r'<li class="country[^"]*".*?</li>', html, re.DOTALL)
print(f"Total country <li> elements: {len(countries)}")
if countries:
    print("First country:", countries[0][:150])
    print("Last country:", countries[-1][:150])

# Also check selected country
sel = re.findall(r'<li class="country[^"]*active[^"]*".*?</li>', html, re.DOTALL)
print(f"Active country elements: {len(sel)}")
if sel:
    print("Active country:", sel[0][:150])

# Check selected country in div or span
dial = re.findall(r'<div class="iti-arrow">.*?</div>|<div class="selected-flag".*?</div>', html, re.DOTALL)
print(f"Selected-flag matches: {len(dial)}")
if dial:
    print("Selected flag snippet:", dial[0][:200])
