import re
import glob
from collections import Counter

slugs = []
for f in sorted(glob.glob('**/*.html', recursive=True)):
    if f.startswith('original'):
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        matches = re.findall(r'linkedin\.com/in/[^"]*', fp.read())
        slugs.extend(matches)

counter = Counter(slugs)
for slug, count in counter.items():
    print(f"{count:4d} {slug}")
