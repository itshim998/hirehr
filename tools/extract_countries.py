import re
import json

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract country list items
# <li class="iti__country iti__preferred iti__active" tabindex="-1" id="iti-0__item-us-preferred" role="option" data-dial-code="1" data-country-code="us" aria-selected="true"><div class="iti__flag-box"><div class="iti__flag iti__us"></div></div><span class="iti__country-name">United States</span><span class="iti__dial-code">+1</span></li>

items = re.findall(r'<li class="iti__country[^"]*"[^>]*data-dial-code="([^"]*)"[^>]*data-country-code="([^"]*)"[^>]*>.*?<span class="iti__country-name">(.*?)</span>.*?<span class="iti__dial-code">(.*?)</span>.*?</li>', html, re.DOTALL)

countries = []
seen = set()
for dial, code, name, dial_display in items:
    key = (code, dial)
    if key not in seen:
        seen.add(key)
        countries.append({
            'code': code.upper(),
            'name': name.strip(),
            'dial': dial_display.strip()
        })

print(f"Extracted {len(countries)} unique countries from original HTML.")
os_dir = 'js'
import os
os.makedirs('js', exist_ok=True)
with open('js/countries.json', 'w', encoding='utf-8') as f:
    json.dump(countries, f, indent=2, ensure_ascii=False)

print("Saved js/countries.json successfully.")
