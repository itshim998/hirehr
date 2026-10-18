import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import base64
import websockets
import shutil
import http.server
import socketserver
import threading
from PIL import Image
import io

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = os.path.join("docs", "screenshots", "design")

PAGES = [
    ("home", "index.html"),
    ("about_us", "about-us/index.html"),
    ("our_speciality", "our-specialty/index.html"),
    ("contact_us", "contact-us/index.html"),
    ("404", "404.html")
]

VIEWPORTS = [
    (375, 812, True),
    (768, 1024, False),
    (1280, 900, False),
    (1920, 1080, False)
]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server(port):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

async def run_automation():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    server_port = 8089
    server = start_server(server_port)
    base_url = f"http://127.0.0.1:{server_port}"

    cdp_port = 9226
    user_data = os.path.abspath("tmp_chrome_design")
    chrome_cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    proc = subprocess.Popen(chrome_cmd)
    time.sleep(2)

    console_errors = []
    test_results = {}

    try:
        new_tab_req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json/new", method="PUT")
        with urllib.request.urlopen(new_tab_req) as resp:
            tab = json.loads(resp.read().decode())
        ws_url = tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("method") == "Runtime.exceptionThrown":
                        console_errors.append(data)
                    if data.get("id") == msg_id:
                        return data.get("result", {})

            await send("Page.enable")
            await send("Runtime.enable")
            await send("Network.enable")

            print("1. Capturing screenshots across 5 pages at 4 viewports (375, 768, 1280, 1920)...")
            for page_name, page_path in PAGES:
                url = f"{base_url}/{page_path}"
                await send("Page.navigate", {"url": url})
                await asyncio.sleep(1.0)

                for width, height, is_mobile in VIEWPORTS:
                    await send("Emulation.setDeviceMetricsOverride", {
                        "width": width,
                        "height": height,
                        "deviceScaleFactor": 1,
                        "mobile": is_mobile
                    })
                    await send("Emulation.setVisibleSize", {"width": width, "height": height})
                    await asyncio.sleep(0.5)

                    # Trigger any reveal animations
                    await send("Runtime.evaluate", {
                        "expression": "document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-revealed'));"
                    })
                    await asyncio.sleep(0.2)

                    shot = await send("Page.captureScreenshot", {"format": "png"})
                    if shot and "data" in shot:
                        raw_bytes = base64.b64decode(shot["data"])
                        img = Image.open(io.BytesIO(raw_bytes))
                        out_path = os.path.join(OUTPUT_DIR, f"{page_name}_{width}px.webp")
                        img.save(out_path, "WEBP", quality=82, method=6)
                        print(f"  [SAVED] {out_path} ({os.path.getsize(out_path):,} bytes)")

            # Total folder size
            total_size = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in os.listdir(OUTPUT_DIR))
            test_results["screenshots_total_bytes"] = total_size
            print(f"\nTotal screenshots size: {total_size / 1024 / 1024:.2f} MB (Budget: < 3.0 MB)")

            # 2. Test Mobile Menu & Keyboard Walkthrough
            print("\n2. Testing Mobile Menu & Keyboard Navigation...")
            await send("Page.navigate", {"url": f"{base_url}/index.html"})
            await asyncio.sleep(0.8)
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 375,
                "height": 812,
                "deviceScaleFactor": 1,
                "mobile": True
            })
            await asyncio.sleep(0.3)

            # Click nav toggle
            toggle_state = (await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = document.querySelector('.nav-toggle');
                    btn.click();
                    const nav = document.querySelector('.main-navigation');
                    const expanded = btn.getAttribute('aria-expanded');
                    const active = nav.classList.contains('is-active');
                    const bodyLocked = document.body.style.overflow === 'hidden';
                    return { expanded, active, bodyLocked };
                })()
                """,
                "returnByValue": True
            })).get("result", {}).get("value")
            print("  Mobile open result:", toggle_state)
            test_results["mobile_menu_open"] = toggle_state

            # Escape key dismissal
            esc_state = (await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const event = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true });
                    document.dispatchEvent(event);
                    const btn = document.querySelector('.nav-toggle');
                    const nav = document.querySelector('.main-navigation');
                    const expanded = btn.getAttribute('aria-expanded');
                    const active = nav.classList.contains('is-active');
                    const bodyUnlocked = document.body.style.overflow === '';
                    return { expanded, active, bodyUnlocked, focused: document.activeElement === btn };
                })()
                """,
                "returnByValue": True
            })).get("result", {}).get("value")
            print("  Mobile Esc result:", esc_state)
            test_results["mobile_menu_esc"] = esc_state

            # 3. Test Blocked ui.js
            print("\n3. Testing Fallback with ui.js Blocked...")
            await send("Network.setBlockedURLs", {"urls": ["*ui.js*"]})
            await send("Page.navigate", {"url": f"{base_url}/about-us/index.html"})
            await asyncio.sleep(1.0)
            blocked_state = (await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const el = document.querySelector('.page-body');
                    const style = window.getComputedStyle(el);
                    return {
                        opacity: style.opacity,
                        visibility: style.visibility,
                        display: style.display,
                        isRevealedClassPresent: el.classList.contains('is-revealed'),
                        hasRevealOnHtml: document.documentElement.classList.contains('has-reveal')
                    };
                })()
                """,
                "returnByValue": True
            })).get("result", {}).get("value")
            print("  Blocked ui.js body visibility:", blocked_state)
            test_results["blocked_uijs_visibility"] = blocked_state
            await send("Network.setBlockedURLs", {"urls": []})

            # 4. Test Reduced Motion
            print("\n4. Testing prefers-reduced-motion...")
            await send("Emulation.setEmulatedMedia", {
                "features": [{"name": "prefers-reduced-motion", "value": "reduce"}]
            })
            await send("Page.navigate", {"url": f"{base_url}/index.html"})
            await asyncio.sleep(0.8)
            reduced_state = (await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const el = document.querySelector('[data-reveal]');
                    const style = el ? window.getComputedStyle(el) : null;
                    return {
                        matchesMedia: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                        transitionDuration: style ? style.transitionDuration : null,
                        transform: style ? style.transform : null
                    };
                })()
                """,
                "returnByValue": True
            })).get("result", {}).get("value")
            print("  Reduced motion status:", reduced_state)
            test_results["reduced_motion"] = reduced_state

            # Console errors
            test_results["console_errors_count"] = len(console_errors)
            test_results["console_errors"] = console_errors
            print(f"\nConsole Errors Count: {len(console_errors)}")

    finally:
        server.shutdown()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        if os.path.exists(user_data):
            try:
                shutil.rmtree(user_data, ignore_errors=True)
            except Exception:
                pass

    with open("docs/test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)
    print("\nSaved automation test results to docs/test_results.json")

if __name__ == "__main__":
    asyncio.run(run_automation())
