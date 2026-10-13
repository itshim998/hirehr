import urllib.request
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

os.makedirs('assets', exist_ok=True)

url = "https://web.archive.org/web/20220523025133if_/https://www.hirehrconsultancy.com/wp-content/uploads/2021/07/cropped-Capture-32x32.png"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        content = resp.read()
        print(f"Downloaded cropped-Capture-32x32.png: {len(content)} bytes")
        with open('assets/cropped-Capture-32x32.png', 'wb') as f:
            f.write(content)
except Exception as e:
    print(f"Failed to download cropped-Capture-32x32.png: {e}")
