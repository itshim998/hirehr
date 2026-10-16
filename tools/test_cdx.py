import urllib.request
import json
import time
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

time.sleep(2)
cdx_url = "https://web.archive.org/cdx/search/cdx?url=hirehrconsultancy.com/*&output=json&limit=50"
req = urllib.request.Request(cdx_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        content = resp.read().decode('utf-8')
        data = json.loads(content)
        print(f"CDX returned {len(data)} entries:")
        for row in data[:15]:
            print("  ", row)
except Exception as e:
    print(f"CDX query failed: {e}")
