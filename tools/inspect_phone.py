import re

with open('original/index.original.html', 'r', encoding='utf-8') as f:
    html = f.read()

# find wpforms phone field area
m = re.search(r'wpforms-308-field_5.*?(?=<div class="wpforms-field |</form>)', html, re.DOTALL)
if m:
    print("Phone field section:")
    print(m.group(0)[:1500])
else:
    print("Not found phone field section directly, search broader:")
    for line in html.splitlines():
        if 'field_5' in line or 'country' in line.lower() or 'iti' in line.lower():
            print(line[:200])
