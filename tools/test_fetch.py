import urllib.request
import urllib.error
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls_to_test = [
    "https://hirehrconsultancy.com/wp-content/uploads/2021/07/Logo-Edited-1.png",
    "https://hirehrconsultancy.com/wp-content/uploads/2021/07/Image-Consultant-Course-1024x682.jpg",
    "https://hirehrconsultancy.com/wp-content/uploads/elementor/css/post-8.css",
    "https://hirehrconsultancy.com/wp-content/uploads/elementor/css/global.css",
]

print("=== TESTING LIVE DOMAIN ===")
for u in urls_to_test:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            print(f"LIVE SUCCESS: {u} -> Status {resp.status}, length {len(resp.read())}")
    except Exception as e:
        print(f"LIVE FAILED: {u} -> {e}")

print("\n=== TESTING WAYBACK MACHINE AVAILABILITY API ===")
for u in urls_to_test:
    try:
        api_url = f"https://archive.org/wayback/available?url={u}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            snaps = data.get('archived_snapshots', {})
            closest = snaps.get('closest', {})
            if closest and closest.get('available'):
                print(f"WAYBACK FOUND: {u} -> {closest.get('url')} (timestamp {closest.get('timestamp')})")
            else:
                print(f"WAYBACK NOT FOUND: {u}")
    except Exception as e:
        print(f"WAYBACK API ERROR: {u} -> {e}")
