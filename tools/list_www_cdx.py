import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cdx_url = "https://web.archive.org/cdx/search/cdx?url=www.hirehrconsultancy.com/*&output=json"
req = urllib.request.Request(cdx_url, headers={
    'User-Agent': 'Mozilla/5.0'
})

with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
    content = resp.read().decode('utf-8')
    data = json.loads(content)

print(f"Total rows for www: {len(data)}")
for row in data:
    print(row[1], row[2], row[3], row[4])
