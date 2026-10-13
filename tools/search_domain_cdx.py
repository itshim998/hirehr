import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Let's search domain match
cdx_url = "https://web.archive.org/cdx/search/cdx?url=hirehrconsultancy.com&matchType=domain&output=json"
req = urllib.request.Request(cdx_url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        content = resp.read().decode('utf-8')
        data = json.loads(content)
        print(f"Total entries across entire domain: {len(data)}")
        with open('tools/all_domain_cdx.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
except Exception as e:
    print(f"Domain CDX failed: {e}")
