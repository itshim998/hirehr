import json
import html

with open('js/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

for c in countries:
    c['name'] = html.unescape(c['name'])

with open('js/countries.js', 'w', encoding='utf-8') as f:
    f.write("// Extracted country list from original WPForms international phone field\n")
    f.write("window.COUNTRY_DATA = ")
    json.dump(countries, f, indent=2, ensure_ascii=False)
    f.write(";\n")

print("Created js/countries.js successfully.")
