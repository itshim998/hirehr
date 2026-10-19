import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import websockets
import http.server
import threading

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server(port):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

async def run_tests():
    server_port = 8092
    server = start_server(server_port)
    base_url = f"http://127.0.0.1:{server_port}"
    cdp_port = 9227
    user_data = os.path.abspath("tmp_chrome_nav_test")

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

    try:
        new_tab_req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json/new", method="PUT")
        with urllib.request.urlopen(new_tab_req) as resp:
            tab = json.loads(resp.read().decode())
        ws_url = tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=10 * 1024 * 1024) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == msg_id:
                        return data.get("result", {})

            await send("Page.enable")
            await send("Runtime.enable")

            pages = [
                ("homepage", "index.html"),
                ("inner-page", "about-us/index.html")
            ]
            widths = [360, 390, 768]
            scrolls = [0, 900]

            all_passed = True

            for page_name, page_path in pages:
                url = f"{base_url}/{page_path}"
                for w in widths:
                    for s in scrolls:
                        # Navigate
                        await send("Page.navigate", {"url": url})
                        await asyncio.sleep(0.4)

                        # Set viewport
                        await send("Emulation.setDeviceMetricsOverride", {
                            "width": w,
                            "height": 800,
                            "deviceScaleFactor": 1,
                            "mobile": True
                        })
                        await asyncio.sleep(0.2)

                        # Scroll
                        if s > 0:
                            await send("Runtime.evaluate", {
                                "expression": f"window.scrollTo(0, {s});"
                            })
                            await asyncio.sleep(0.2)

                        # Open mobile menu by clicking .nav-toggle
                        open_res = await send("Runtime.evaluate", {
                            "expression": """
                            (() => {
                                const toggle = document.querySelector('.nav-toggle');
                                if (!toggle) return { error: 'No toggle' };
                                toggle.click();
                                return {
                                    isOpen: document.body.classList.contains('nav-open'),
                                    isExpanded: toggle.getAttribute('aria-expanded') === 'true'
                                };
                            })()
                            """,
                            "returnByValue": True
                        })
                        val = open_res.get("result", {}).get("value", {})
                        if not val.get("isOpen"):
                            print(f"[FAIL] {page_name} @ {w}px, scroll {s}: Menu failed to open")
                            all_passed = False
                            continue

                        await asyncio.sleep(0.2)

                        # Check elementFromPoint at center of .nav-toggle
                        hit_test = await send("Runtime.evaluate", {
                            "expression": """
                            (() => {
                                const toggle = document.querySelector('.nav-toggle');
                                const rect = toggle.getBoundingClientRect();
                                const cx = rect.left + rect.width / 2;
                                const cy = rect.top + rect.height / 2;
                                const elAtPoint = document.elementFromPoint(cx, cy);
                                const isToggle = elAtPoint === toggle || elAtPoint.closest('.nav-toggle') === toggle;
                                
                                const wordmark = document.querySelector('.brand-wordmark');
                                const toggleColor = window.getComputedStyle(toggle).color;
                                const wordmarkColor = wordmark ? window.getComputedStyle(wordmark).color : '';
                                
                                return {
                                    cx, cy,
                                    elTag: elAtPoint ? elAtPoint.tagName : null,
                                    elClass: elAtPoint ? elAtPoint.className : null,
                                    isToggle,
                                    toggleColor,
                                    wordmarkColor
                                };
                            })()
                            """,
                            "returnByValue": True
                        })
                        hit_val = hit_test.get("result", {}).get("value", {})
                        if not hit_val.get("isToggle"):
                            print(f"[FAIL] {page_name} @ {w}px, scroll {s}: elementFromPoint returned {hit_val.get('elTag')}.{hit_val.get('elClass')} instead of .nav-toggle")
                            all_passed = False
                        else:
                            print(f"[PASS] {page_name} @ {w}px, scroll {s}: elementFromPoint => {hit_val.get('elTag')}.{hit_val.get('elClass')} (isToggle=True), wordmark={hit_val.get('wordmarkColor')}, toggle={hit_val.get('toggleColor')}")

                        # Click again to close
                        close_res = await send("Runtime.evaluate", {
                            "expression": """
                            (() => {
                                const toggle = document.querySelector('.nav-toggle');
                                toggle.click();
                                return {
                                    isOpen: document.body.classList.contains('nav-open'),
                                    isExpanded: toggle.getAttribute('aria-expanded') === 'true'
                                };
                            })()
                            """,
                            "returnByValue": True
                        })
                        cval = close_res.get("result", {}).get("value", {})
                        if cval.get("isOpen"):
                            print(f"[FAIL] {page_name} @ {w}px, scroll {s}: Menu failed to close upon clicking toggle")
                            all_passed = False

            if all_passed:
                print("\nALL MOBILE NAV TESTS PASSED (12 of 12 conditions)!")
                return 0
            else:
                print("\nSOME MOBILE NAV TESTS FAILED!")
                return 1

    finally:
        proc.kill()
        server.shutdown()

if __name__ == "__main__":
    code = asyncio.run(run_tests())
    sys.exit(code)
