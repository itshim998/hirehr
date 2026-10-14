import os
import re

files_to_update = [
    'index.html',
    '404.html',
    'sitemap.xml',
    'robots.txt',
    'css/style.css',
    'js/main.js',
    'README.md',
    'tools/build_inner_pages.py'
]

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Company Name replacements:
    # "HireHR Consultancy Services" -> "HireHR Services"
    content = re.sub(r'HireHR\s+Consultancy\s+Services', 'HireHR Services', content)
    # "HireHR consultancy services" -> "HireHR services"
    content = re.sub(r'HireHR\s+consultancy\s+services', 'HireHR services', content)
    # "HireHR Consultancy services" -> "HireHR Services"
    content = re.sub(r'HireHR\s+Consultancy\s+services', 'HireHR Services', content)

    # 2. LinkedIn URL:
    # "hirehr-consultancy-services" -> "hirehr-services"
    content = re.sub(r'hirehr-consultancy-services', 'hirehr-services', content)

    # 3. Domain & Email replacements:
    # "hirehrconsultancy.com" -> "hirehrservices.com"
    content = re.sub(r'hirehrconsultancy\.com', 'hirehrservices.com', content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated {path}')

for f in files_to_update:
    if os.path.exists(f):
        update_file(f)

print('Brand rename script completed.')
